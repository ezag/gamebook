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
            pages = GamebookParser(pdf_file).playtime_percentage_pages(True)
            assert [page_num for page_num, _ in pages] == [17, 18]
            for _, layout in pages:
                assert isinstance(layout, LTPage)


def test_extract_teams():
    for gamekey in gamekeys:
        with open(path_to_pdf(gamekey)) as pdf_file:
            assert GamebookParser(pdf_file).extract_teams() == (
                'Green Bay Packers', 'Chicago Bears')


def test_split_teams():

    def indices(left_or_right):
        return [
            [component.index for component in per_page]
            for per_page in left_or_right]

    for gamekey in gamekeys:
        with open(path_to_pdf(gamekey)) as pdf_file:
            left, right, rest = GamebookParser(pdf_file).split_teams()
            left_i, right_i = map(indices, [left, right])
            assert left_i == [[
                    2, 4, 5, 8, 9, 10, 11, 12, 13, 14,
                    15, 16, 17, 18, 19, 20, 21, 43,
            ]]
            assert right_i == [[
                    3, 6, 7, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31,
                    32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42,
                ], [
                    0, 1, 2, 3,
            ]]


def test_extract_playtime_percentage():
    for gamekey in gamekeys:
        with open(path_to_pdf(gamekey)) as pdf_file:
            assert GamebookParser(pdf_file).extract_playtime_percentage() == (
                ('Green Bay Packers', [
                    ('J Sitton'     , 'G' , 59, 100,  0,   0,  5, 19),
                    ('T Lang'       , 'G' , 59, 100,  0,   0,  5, 19),
                    ('B Bulaga'     , 'T' , 59, 100,  0,   0,  5, 19),
                    ('A Rodgers'    , 'QB', 59, 100,  0,   0,  0,  0),
                    ('D Bakhtiari'  , 'T' , 59, 100,  0,   0,  0,  0),
                    ('C Linsley'    , 'C' , 59, 100,  0,   0,  0,  0),
                    ('D Adams'      , 'WR', 57,  97,  0,   0,  1,  4),
                    ('J Jones'      , 'WR', 54,  92,  0,   0,  0,  0),
                    ('R Cobb'       , 'WR', 53,  90,  0,   0,  0,  0),
                    ('E Lacy'       , 'RB', 45,  76,  0,   0,  0,  0),
                    ('R Rodgers'    , 'TE', 37,  63,  0,   0,  8, 31),
                    ('A Quarless'   , 'TE', 23,  39,  0,   0,  3, 12),
                    ('J Starks'     , 'RB', 13,  22,  0,   0,  6, 23),
                    ('J Kuhn'       , 'FB',  7,  12,  0,   0,  6, 23),
                    ('J Walker'     , 'G' ,  3,   5,  0,   0,  5, 19),
                    ('J Tretter'    , 'C' ,  1,   2,  0,   0, 11, 42),
                    ('J Janis'      , 'WR',  1,   2,  0,   0,  9, 35),
                    ('T Montgomery' , 'WR',  1,   2,  0,   0,  5, 19),
                    ('H Clinton-Dix', 'FS',  0,   0, 73, 100, 14, 54),
                    ('M Hyde'       , 'FS',  0,   0, 73, 100,  8, 31),
                    ('C Matthews'   , 'LB',  0,   0, 73, 100,  6, 23),
                    ('S Shields'    , 'CB',  0,   0, 72,  99, 13, 50),
                    ('C Hayward'    , 'CB',  0,   0, 62,  85,  6, 23),
                    ('N Palmer'     , 'LB',  0,   0, 58,  79, 14, 54),
                    ('D Randall'    , 'CB',  0,   0, 57,  78,  1,  4),
                    ('M Daniels'    , 'DT',  0,   0, 55,  75,  6, 23),
                    ('M Neal'       , 'LB',  0,   0, 52,  71,  6, 23),
                    ('J Peppers'    , 'LB',  0,   0, 52,  71,  6, 23),
                    ('B Raji'       , 'NT',  0,   0, 44,  60, 11, 42),
                    ('N Perry'      , 'LB',  0,   0, 30,  41,  0,  0),
                    ('S Richardson' , 'SS',  0,   0, 28,  38, 15, 58),
                    ('J Boyd'       , 'NT',  0,   0, 23,  32,  5, 19),
                    ('J Elliott'    , 'LB',  0,   0, 18,  25, 21, 81),
                    ('S Barrington' , 'LB',  0,   0, 15,  21,  1,  4),
                    ('M Pennel'     , 'DE',  0,   0, 13,  18,  0,  0),
                    ('B Gaston'     , 'DT',  0,   0,  5,   7,  0,  0),
                    ('J Ryan'       , 'LB',  0,   0,  0,   0, 14, 54),
                    ('C Banjo'      , 'SS',  0,   0,  0,   0, 14, 54),
                    ('A Ripkowski'  , 'FB',  0,   0,  0,   0, 12, 46),
                    ('M Crosby'     , 'K' ,  0,   0,  0,   0, 11, 42),
                    ('D Goodson'    , 'CB',  0,   0,  0,   0,  9, 35),
                    ('B Goode'      , 'LS',  0,   0,  0,   0,  7, 27),
                    ('T Masthay'    , 'P' ,  0,   0,  0,   0,  7, 27),
                    ('D Barclay'    , 'T' ,  0,   0,  0,   0,  5, 19),
                    ('Q Rollins'    , 'CB',  0,   0,  0,   0,  5, 19),
                ]),
                ('Chicago Bears', [
                ]))
