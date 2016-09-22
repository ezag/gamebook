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
        start_index = None
        for page_num, page in reversed(pages):
            interpreter.process_page(page)
            layout = list(device.get_result())
            obj = layout[0]
            if obj.get_text().strip() == 'Playtime Percentage':
                start_index = page_num - 1
                break
        if start_index is None:
            raise MissingPlaytimePercentage
        return pages[start_index:]
