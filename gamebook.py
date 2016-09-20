from __future__ import print_function

import sys

from pdfminer.layout import LAParams
from pdfminer.converter import PDFPageAggregator
from pdfminer.pdfdevice import PDFDevice
from pdfminer.pdfdocument import PDFDocument
from pdfminer.pdfinterp import PDFPageInterpreter, PDFResourceManager
from pdfminer.pdfpage import PDFPage, PDFTextExtractionNotAllowed
from pdfminer.pdfparser import PDFParser


if __name__ == '__main__':
    parser = PDFParser(sys.stdin)
    document = PDFDocument(parser)
    if not document.is_extractable:
        raise PDFTextExtractionNotAllowed
    resource_manager = PDFResourceManager()
    laparams = LAParams()
    device = PDFPageAggregator(resource_manager, laparams=laparams)
    interpreter = PDFPageInterpreter(resource_manager, device)
    pages = PDFPage.create_pages(document)
    print('Looking for page with Playtime Percentage...', file=sys.stderr)
    for i, page in enumerate(pages, 1):
        print('  page {}...'.format(i), end='', file=sys.stderr)
        interpreter.process_page(page)
        layout = list(device.get_result())
        obj = layout[0]
        if obj.get_text().strip() != 'Playtime Percentage':
            print(' not found')
            continue
        print(' found\n')
        players = layout[43].get_text().split('\n')
        position = layout[10].get_text().split('\n')
        off_snaps = layout[8].get_text().split('\n')
        off_pct = layout[9].get_text().split('\n')
        print('{:20} {:10} {:12} {:12}\n'.format(
            'player', 'position', 'off_snaps', 'off_pct'))
        for p, pos, os, op in zip(players, position, off_snaps, off_pct):
            print('{:20} {:10} {:12} {:12}'.format(p, pos, os, op))
        break
