from __future__ import division

from collections import namedtuple

from enum import Enum
from pdfminer.layout import LAParams, LTTextBoxHorizontal
from pdfminer.converter import PDFPageAggregator
from pdfminer.pdfdocument import PDFDocument
from pdfminer.pdfinterp import PDFPageInterpreter, PDFResourceManager
from pdfminer.pdfpage import PDFPage, PDFTextExtractionNotAllowed
from pdfminer.pdfparser import PDFParser


PlaytimePercentage = namedtuple('PlaytimePercentage', (
    'player_name',
    'position',
    'off_snaps',
    'off_pct',
    'def_snaps',
    'def_pct',
    'spt_snaps',
    'spt_pct',
))


ComponentType = Enum(  # pylint: disable=invalid-name
    'ComponentType',
    ' '.join((
        'team_name',
        'off_header',
        'def_spt_header',
        'player_column',
        'position_column',
        'numeric_column',
        'percentage_column',
        'dual_column',
    )))


Column = Enum(  # pylint: disable=invalid-name
    'Column',
    ' '.join((
        'offense',
        'defense',
        'special_teams',
    )))


class MissingPlaytimePercentage(Exception):
    pass


class Grid(object):

    def __init__(self):
        self.y_0 = []
        self.y_delta = []
        self.x_off = None
        self.x_def = None
        self.x_spt = None

    @classmethod
    def from_components(cls, components):
        # pylint: disable=no-member
        grid = cls()
        for component in components[0]:
            if (
                    GamebookParser.type_from_text(component.get_text()) ==
                    ComponentType.off_header
            ):
                grid.x_off = (component.x0 + component.x1) / 2
            if (
                    GamebookParser.type_from_text(component.get_text()) ==
                    ComponentType.def_spt_header
            ):
                grid.x_def = (3 * component.x0 + component.x1) / 4
                grid.x_spt = (component.x0 + 3 * component.x1) / 4
        for page in components:
            for component in page:
                if (
                        GamebookParser.type_from_text(component.get_text()) ==
                        ComponentType.player_column
                ):
                    rows_num = len(component.get_text().strip().split('\n'))
                    grid.y_0.append(component.y1)
                    grid.y_delta.append(
                        (component.y1 - component.y0) / rows_num)
        for value in (grid.x_off, grid.x_def, grid.x_spt):
            if value is None:
                raise ValueError('Unable to derive full grid from components')
        for value in (grid.y_0, grid.y_delta):
            if len(value) < len(components):
                raise ValueError('Unable to derive full grid from components')
        return grid

    def column_for(self, component):
        # pylint: disable=no-member
        column = Column.offense
        x = (component.x0 + component.x1) / 2
        delta = abs(x - self.x_off)
        if abs(x - self.x_def) < delta:
            delta = abs(x - self.x_def)
            column = Column.defense
        if abs(x - self.x_spt) < delta:
            delta = abs(x - self.x_spt)
            column = Column.special_teams
        return column

    def top_index(self, component, page_num=0):
        return int(
            (self.y_0[page_num] - component.y1) // self.y_delta[page_num])


class GamebookParser(object):

    def __init__(self, pdf_file):
        self.pdf_file = pdf_file
        self._playtime_percentage_pages = None

    def pages(self):
        document = PDFDocument(PDFParser(self.pdf_file))
        if not document.is_extractable:
            raise PDFTextExtractionNotAllowed
        return PDFPage.create_pages(document)

    def playtime_percentage_pages(self, with_page_nums=False):
        if self._playtime_percentage_pages is None:
            resource_manager = PDFResourceManager()
            device = PDFPageAggregator(resource_manager, laparams=LAParams())
            interpreter = PDFPageInterpreter(resource_manager, device)
            pages = list(enumerate(self.pages(), 1))
            start_page_num = None
            layouts = []
            for page_num, page in reversed(pages):
                interpreter.process_page(page)
                layout = device.get_result()
                layouts.append(layout)
                obj = iter(layout).next()
                if obj.get_text().strip() == 'Playtime Percentage':
                    start_page_num = page_num
                    break
            if start_page_num is None:
                raise MissingPlaytimePercentage
            page_numbers = range(start_page_num, len(pages) + 1)
            assert len(layouts) == len(page_numbers)
            layouts.reverse()
            self._playtime_percentage_pages = zip(page_numbers, layouts)
        return (
            self._playtime_percentage_pages if with_page_nums else
            [page for _, page in self._playtime_percentage_pages])

    def split_teams(self):
        pages = self.playtime_percentage_pages()
        left_all, right_all, rest_all = [], [], []
        for page in pages:
            left, right, rest = [], [], []
            x_center = (page.x1 - page.x0) / 2
            for component in page:
                target = rest
                if isinstance(component, LTTextBoxHorizontal):
                    if component.x1 <= x_center:
                        target = left
                    elif component.x0 >= x_center:
                        target = right
                target.append(component)
            if left:
                left_all.append(left)
            if right:
                right_all.append(right)
            if rest:
                rest_all.append(rest)
        return left_all, right_all, rest_all

    @staticmethod
    def type_from_text(text):
        # pylint: disable=no-member
        component_type = ComponentType.team_name
        lines = text.strip().split('\n')
        head = lines[0]
        if head == 'Offense':
            component_type = ComponentType.off_header
        elif head == 'Defense Special Teams':
            component_type = ComponentType.def_spt_header
        elif head.isdigit():
            component_type = ComponentType.numeric_column
        elif head.endswith('%') and head.rstrip('%').isdigit():
            component_type = ComponentType.percentage_column
        elif head.isalpha() and len(head) <= 2 and head.isupper():
            component_type = ComponentType.position_column
        else:
            fst, snd = head.split(' ', 3)[:2]
            if (
                    fst.isdigit() and snd.endswith('%') and
                    snd.rstrip('%').isdigit()
            ):
                component_type = ComponentType.dual_column
            if len(fst) == 1 and fst.isalpha() and snd.isalpha():
                component_type = ComponentType.player_column
        return component_type

    @classmethod
    def extract_playtime_percentage_team(cls, components):
        grid = Grid.from_components(components)
        player_name_column = []
        position_column = []
        off_snaps_column = []
        off_pct_column = []
        def_snaps_column = []
        def_pct_column = []
        spt_snaps_column = []
        spt_pct_column = []
        team_name = None
        for i, page in enumerate(components):
            first_row = len(player_name_column)
            for component in page:
                text = component.get_text().strip()
                component_type = GamebookParser.type_from_text(text)
                if component_type == ComponentType.team_name:
                    team_name = text
                elif component_type == ComponentType.player_column:
                    player_name_column.extend(text.split('\n'))
                elif component_type == ComponentType.position_column:
                    position_column.extend(text.split('\n'))
                elif component_type in (
                        ComponentType.numeric_column,
                        ComponentType.percentage_column,
                        ComponentType.dual_column,
                ):
                    numeric_column, percentage_column = {
                        Column.offense: (off_snaps_column, off_pct_column),
                        Column.defense: (def_snaps_column, def_pct_column),
                        Column.special_teams: (
                            spt_snaps_column, spt_pct_column),
                    }[grid.column_for(component)]
                    top_index = grid.top_index(component)
                    if component_type == ComponentType.numeric_column:
                        numeric_column.extend(
                            [0] * (top_index - len(numeric_column)))
                        numeric_column.extend(map(int, text.split('\n')))
                    elif component_type == ComponentType.percentage_column:
                        percentage_column.extend(
                            [0] * (top_index - len(percentage_column)))
                        percentage_column.extend([
                            int(row.rstrip('%'))
                            for row in text.split('\n')])
                    elif component_type == ComponentType.dual_column:
                        numeric_column.extend(
                            [0] * (top_index - len(numeric_column)))
                        percentage_column.extend(
                            [0] * (top_index - len(percentage_column)))
                        splitted = text.split()
                        numeric = splitted[::2]
                        percentage = splitted[1::2]
                        for i in range(len(numeric)):
                            if numeric[i].endswith('%'):
                                numeric[i], percentage[i] = (
                                    percentage[i], numeric[i])
                        numeric_column.extend(map(int, numeric))
                        percentage_column.extend([
                            int(row.rstrip('%')) for row in percentage])
        for column in (
                off_snaps_column,
                off_pct_column,
                def_snaps_column,
                def_pct_column,
                spt_snaps_column,
                spt_pct_column,
        ):
            column.extend(
                [0] * (len(player_name_column) - len(column)))
        return (
            team_name,
            [PlaytimePercentage(*row) for row in zip(
                player_name_column,
                position_column,
                off_snaps_column,
                off_pct_column,
                def_snaps_column,
                def_pct_column,
                spt_snaps_column,
                spt_pct_column,
            )])

    def extract_playtime_percentage(self):
        left, right, _ = self.split_teams()
        return (
            self.extract_playtime_percentage_team(left),
            self.extract_playtime_percentage_team(right))
