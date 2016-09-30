import os.path

from pdfminer.layout import LTPage

from gamebook.parse import Column, GamebookParser, Grid


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


def test_grid_columns():
    for gamekey in gamekeys:
        with open(path_to_pdf(gamekey)) as pdf_file:
            left, right, _ = GamebookParser(pdf_file).split_teams()
            grid = Grid.from_components(left)
            for component in left[0]:
                if component.index in (
                        8, 9,
                ):
                    assert grid.column_for(component) == Column.offense
                elif component.index in (
                        11,
                ):
                    assert grid.column_for(component) == Column.defense
                elif component.index in (
                        12, 13, 14, 15, 16, 17, 18, 19, 20, 21,
                ):
                    assert grid.column_for(component) == Column.special_teams
            grid = Grid.from_components(right)
            for component in right[0]:
                if component.index in (
                        23, 24, 
                ):
                    assert grid.column_for(component) == Column.offense
                elif component.index in (
                        26, 
                ):
                    assert grid.column_for(component) == Column.defense
                elif component.index in (
                        27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39,
                        40, 41, 42,
                ):
                    assert grid.column_for(component) == Column.special_teams
            for component in right[1]:
                if component.index in (
                        2, 3,
                ):
                    assert grid.column_for(component) == Column.special_teams


def test_grid_rows():
    for gamekey in gamekeys:
        with open(path_to_pdf(gamekey)) as pdf_file:
            left, right, _ = GamebookParser(pdf_file).split_teams()
            grid = Grid.from_components(left)
            for component in left[0]:
                if component.index in (
                        8, 9, 12, 13,
                ):
                    assert grid.top_index(component) == 0
                if component.index in (
                        14, 15,
                ):
                    assert grid.top_index(component) == 6
                if component.index in (
                        16, 19,
                ):
                    assert grid.top_index(component) == 10
                if component.index in (
                        11,
                ):
                    assert grid.top_index(component) == 18
                if component.index in (
                        17, 20,
                ):
                    assert grid.top_index(component) == 30
                if component.index in (
                        18, 21,
                ):
                    assert grid.top_index(component) == 36
            grid = grid.from_components(right)
            for component in right[0]:
                if component.index in (
                        23, 24, 27, 31,
                ):
                    assert grid.top_index(component) == 0
                if component.index in (
                        28, 32,
                ):
                    assert grid.top_index(component) == 6
                if component.index in (
                        29, 33,
                ):
                    assert grid.top_index(component) == 11
                if component.index in (
                        30, 34,
                ):
                    assert grid.top_index(component) == 13
                if component.index in (
                        26,
                ):
                    assert grid.top_index(component) == 18
                if component.index in (
                        35, 36,
                ):
                    assert grid.top_index(component) == 22
                if component.index in (
                        37, 40,
                ):
                    assert grid.top_index(component) == 24
                if component.index in (
                        38, 41,
                ):
                    assert grid.top_index(component) == 27
                if component.index in (
                        39, 42,
                ):
                    assert grid.top_index(component) == 32
            for component in right[1]:
                if component.index in (
                        2, 3,
                ):
                    assert grid.top_index(component, 1) == 0


def test_extract_playtime_percentage():
    for gamekey in gamekeys:
        with open(path_to_pdf(gamekey)) as pdf_file:
            assert GamebookParser(pdf_file).extract_playtime_percentage() == (
                (u'Green Bay Packers', [
                    (u'J Sitton'     , u'G' , 59, 100,  0,   0,  5, 19),
                    (u'T Lang'       , u'G' , 59, 100,  0,   0,  5, 19),
                    (u'B Bulaga'     , u'T' , 59, 100,  0,   0,  5, 19),
                    (u'A Rodgers'    , u'QB', 59, 100,  0,   0,  0,  0),
                    (u'D Bakhtiari'  , u'T' , 59, 100,  0,   0,  0,  0),
                    (u'C Linsley'    , u'C' , 59, 100,  0,   0,  0,  0),
                    (u'D Adams'      , u'WR', 57,  97,  0,   0,  1,  4),
                    (u'J Jones'      , u'WR', 54,  92,  0,   0,  0,  0),
                    (u'R Cobb'       , u'WR', 53,  90,  0,   0,  0,  0),
                    (u'E Lacy'       , u'RB', 45,  76,  0,   0,  0,  0),
                    (u'R Rodgers'    , u'TE', 37,  63,  0,   0,  8, 31),
                    (u'A Quarless'   , u'TE', 23,  39,  0,   0,  3, 12),
                    (u'J Starks'     , u'RB', 13,  22,  0,   0,  6, 23),
                    (u'J Kuhn'       , u'FB',  7,  12,  0,   0,  6, 23),
                    (u'J Walker'     , u'G' ,  3,   5,  0,   0,  5, 19),
                    (u'J Tretter'    , u'C' ,  1,   2,  0,   0, 11, 42),
                    (u'J Janis'      , u'WR',  1,   2,  0,   0,  9, 35),
                    (u'T Montgomery' , u'WR',  1,   2,  0,   0,  5, 19),
                    (u'H Clinton-Dix', u'FS',  0,   0, 73, 100, 14, 54),
                    (u'M Hyde'       , u'FS',  0,   0, 73, 100,  8, 31),
                    (u'C Matthews'   , u'LB',  0,   0, 73, 100,  6, 23),
                    (u'S Shields'    , u'CB',  0,   0, 72,  99, 13, 50),
                    (u'C Hayward'    , u'CB',  0,   0, 62,  85,  6, 23),
                    (u'N Palmer'     , u'LB',  0,   0, 58,  79, 14, 54),
                    (u'D Randall'    , u'CB',  0,   0, 57,  78,  1,  4),
                    (u'M Daniels'    , u'DT',  0,   0, 55,  75,  6, 23),
                    (u'M Neal'       , u'LB',  0,   0, 52,  71,  6, 23),
                    (u'J Peppers'    , u'LB',  0,   0, 52,  71,  6, 23),
                    (u'B Raji'       , u'NT',  0,   0, 44,  60, 11, 42),
                    (u'N Perry'      , u'LB',  0,   0, 30,  41,  0,  0),
                    (u'S Richardson' , u'SS',  0,   0, 28,  38, 15, 58),
                    (u'J Boyd'       , u'NT',  0,   0, 23,  32,  5, 19),
                    (u'J Elliott'    , u'LB',  0,   0, 18,  25, 21, 81),
                    (u'S Barrington' , u'LB',  0,   0, 15,  21,  1,  4),
                    (u'M Pennel'     , u'DE',  0,   0, 13,  18,  0,  0),
                    (u'B Gaston'     , u'DT',  0,   0,  5,   7,  0,  0),
                    (u'J Ryan'       , u'LB',  0,   0,  0,   0, 14, 54),
                    (u'C Banjo'      , u'SS',  0,   0,  0,   0, 14, 54),
                    (u'A Ripkowski'  , u'FB',  0,   0,  0,   0, 12, 46),
                    (u'M Crosby'     , u'K' ,  0,   0,  0,   0, 11, 42),
                    (u'D Goodson'    , u'CB',  0,   0,  0,   0,  9, 35),
                    (u'B Goode'      , u'LS',  0,   0,  0,   0,  7, 27),
                    (u'T Masthay'    , u'P' ,  0,   0,  0,   0,  7, 27),
                    (u'D Barclay'    , u'T' ,  0,   0,  0,   0,  5, 19),
                    (u'Q Rollins'    , u'CB',  0,   0,  0,   0,  5, 19),
                ]),
                ('Chicago Bears', [
                    (u'J Bushrod'      , u'T' , 73, 100,  0,   0,  6, 23),
                    (u'M Slauson'      , u'G' , 73, 100,  0,   0,  6, 23),
                    (u'V Ducasse'      , u'G' , 73, 100,  0,   0,  6, 23),
                    (u'K Long'         , u'G' , 73, 100,  0,   0,  6, 23),
                    (u'J Cutler'       , u'QB', 73, 100,  0,   0,  0,  0),
                    (u'W Montgomery'   , u'C' , 73, 100,  0,   0,  0,  0),
                    (u'M Bennett'      , u'TE', 70,  96,  0,   0,  6, 23),
                    (u'M Forte'        , u'RB', 65,  89,  0,   0,  0,  0),
                    (u'E Royal'        , u'WR', 61,  84,  0,   0,  0,  0),
                    (u'M Wilson'       , u'WR', 60,  82,  0,   0,  0,  0),
                    (u'A Jeffery'      , u'WR', 56,  77,  0,   0,  0,  0),
                    (u'K Lee'          , u'TE', 11,  15,  0,   0, 13, 50),
                    (u'Z Miller'       , u'TE', 11,  15,  0,   0,  0,  0),
                    (u'J Bellamy'      , u'WR',  8,  11,  0,   0, 15, 58),
                    (u'J Rodgers'      , u'RB',  8,  11,  0,   0,  9, 35),
                    (u'C Leno'         , u'T' ,  6,   8,  0,   0, 10, 38),
                    (u'M Mariani'      , u'WR',  6,   8,  0,   0,  8, 31),
                    (u'J Langford'     , u'RB',  3,   4,  0,   0, 14, 54),
                    (u'A Amos'         , u'S' ,  0,   0, 59, 100,  6, 23),
                    (u'S McClellin'    , u'LB',  0,   0, 59, 100,  6, 23),
                    (u'C Jones'        , u'LB',  0,   0, 59, 100,  5, 19),
                    (u'A Rolle'        , u'S' ,  0,   0, 59, 100,  0,  0),
                    (u'K Fuller'       , u'CB',  0,   0, 58,  98,  4, 15),
                    (u'A Ball'         , u'CB',  0,   0, 58,  98,  0,  0),
                    (u'S McManis'      , u'CB',  0,   0, 54,  92, 10, 38),
                    (u'P McPhee'       , u'LB',  0,   0, 51,  86,  5, 19),
                    (u'J Allen'        , u'LB',  0,   0, 43,  73,  0,  0),
                    (u'W Sutton'       , u'DE',  0,   0, 38,  64, 11, 42),
                    (u'J Jenkins'      , u'DE',  0,   0, 36,  61,  2,  8),
                    (u'E Goldman'      , u'NT',  0,   0, 24,  41,  4, 15),
                    (u'E Ferguson'     , u'DE',  0,   0, 23,  39,  4, 15),
                    (u'W Young'        , u'LB',  0,   0, 20,  34,  0,  0),
                    (u'L Houston'      , u'LB',  0,   0,  4,   7,  5, 19),
                    (u'D Hurst'        , u'S' ,  0,   0,  2,   3,  8, 31),
                    (u'B Vereen'       , u'S' ,  0,   0,  1,   2, 20, 77),
                    (u'C Washington'   , u'DE',  0,   0,  1,   2,  7, 27),
                    (u'L Barrow'       , u'LB',  0,   0,  0,   0, 15, 58),
                    (u'J Timu'         , u'LB',  0,   0,  0,   0, 15, 58),
                    (u'H Jones-Quartey', u'S' ,  0,   0,  0,   0, 12, 46),
                    (u'R Gould'        , u'K' ,  0,   0,  0,   0, 12, 46),
                    (u'B Callahan'     , u'CB',  0,   0,  0,   0,  8, 31),
                    (u'T Mitchell'     , u'CB',  0,   0,  0,   0,  8, 31),
                    (u'T Gafford'      , u'LS',  0,   0,  0,   0,  7, 27),
                    (u"P O'Donnell"    , u'P' ,  0,   0,  0,   0,  7, 27),
                    (u'P Omameh'       , u'G' ,  0,   0,  0,   0,  6, 23),
                ]))
