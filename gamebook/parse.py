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
    'team_name',
)


class MissingPlaytimePercentage(Exception):
    pass


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
        text = text.strip()
        return ComponentType.team_name

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
