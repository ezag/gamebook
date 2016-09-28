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
        self.y_0 = None
        self.y_delta = None
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
        for value in (grid.x_off, grid.x_def, grid.x_spt):
            if value is None:
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

    def extract_teams(self):
        pages = self.playtime_percentage_pages()
        page = list(pages[0])
        return tuple(page[i].get_text().strip() for i in (2, 3))

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

    def extract_playtime_percentage(self):  # pylint: disable=too-many-locals
        pages = map(list, self.playtime_percentage_pages())
        left_team, right_team = self.extract_teams()
        left_player_name_column = pages[0][43].get_text().split('\n')
        #right_player_name_column = pages[0][22].get_text().split('\n')  # XXX
        left_position_column = pages[0][10].get_text().split('\n')
        #right_position_column = pages[0][25].get_text().split('\n')  # XXX
        left_off_snaps_column = map(int, pages[0][8].get_text().strip('\n').split('\n'))
        left_off_snaps_column += [0] * (
            len(left_player_name_column) - len(left_off_snaps_column))
        left_off_pct_column = [
            int(n.rstrip('%')) for n in pages[0][9].get_text().strip('\n').split('\n')]
        left_off_pct_column += [0] * (
            len(left_player_name_column) - len(left_off_pct_column))
        def_snaps_pct = pages[0][11].get_text().strip('\n').split('\n')
        def_snaps_pct[-2:] = [' '.join(def_snaps_pct[-2:])]
        left_def_snaps_column, left_def_pct_column = zip(*[
            row.split(' ') for row in def_snaps_pct])
        left_def_snaps_column = [0] * 18 + map(int, left_def_snaps_column)
        left_def_snaps_column += [0] * (
            len(left_player_name_column) - len(left_def_snaps_column))
        left_def_pct_column = [0] * 18 + [
            int(n.rstrip('%')) for n in left_def_pct_column]
        left_def_pct_column += [0] * (
            len(left_player_name_column) - len(left_def_pct_column))
        left_spt_snaps_column = (
            map(int, pages[0][12].get_text().strip('\n').split('\n')) +
            [0] * 3 +
            map(int, pages[0][14].get_text().strip('\n').split('\n')) +
            [0] * 3 +
            map(int, pages[0][16].get_text().strip('\n').split('\n')) +
            [0] * 1 +
            map(int, pages[0][17].get_text().strip('\n').split('\n')) +
            [0] * 2 +
            map(int, pages[0][18].get_text().strip('\n').split('\n')))
        left_spt_pct_column = (
            [int(n.rstrip('%')) for n in pages[0][13].get_text().strip('\n').split('\n')] +
            [0] * 3 +
            [int(n.rstrip('%')) for n in pages[0][15].get_text().strip('\n').split('\n')] +
            [0] * 3 +
            [int(n.rstrip('%')) for n in pages[0][19].get_text().strip('\n').split('\n')] +
            [0] * 1 +
            [int(n.rstrip('%')) for n in pages[0][20].get_text().strip('\n').split('\n')] +
            [0] * 2 +
            [int(n.rstrip('%')) for n in pages[0][21].get_text().strip('\n').split('\n')])
        return (left_team, zip(
            left_player_name_column,
            left_position_column,
            left_off_snaps_column,
            left_off_pct_column,
            left_def_snaps_column,
            left_def_pct_column,
            left_spt_snaps_column,
            left_spt_pct_column,
        )), (right_team, [
            ])
