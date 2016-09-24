import os.path

from pdfminer.layout import LTPage

from gamebook.parse import GamebookParser


gamekeys = (
    '56505',
)


def path_to_pdf(gamekey):
    return os.path.join(
        os.path.dirname(os.path.realpath(__file__)),
        'pdf',
        '{}.pdf'.format(gamekey))


def test_playtime_percentage_pages():
    for gamekey in gamekeys:
        with open(path_to_pdf(gamekey)) as pdf_file:
            pages = GamebookParser(pdf_file).playtime_percentage_pages()
            assert [page_num for page_num, _ in pages] == [17, 18]
            for _, layout in pages:
                assert isinstance(layout, LTPage)
