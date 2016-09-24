from collections import namedtuple

from pdfminer.layout import LAParams
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


class MissingPlaytimePercentage(Exception):
    pass


class GamebookParser(object):

    def __init__(self, pdf_file):
        self.pdf_file = pdf_file

    def pages(self):
        document = PDFDocument(PDFParser(self.pdf_file))
        if not document.is_extractable:
            raise PDFTextExtractionNotAllowed
        return PDFPage.create_pages(document)

    def playtime_percentage_pages(self):
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
        return zip(page_numbers, layouts)

    def extract_teams(self):
        pages = [page for _, page in self.playtime_percentage_pages()]
        page = list(pages[0])
        return tuple(page[i].get_text().strip() for i in (2, 3))
