import os.path

from pdfminer.layout import LTPage
import pytest

from gamebook.parse import Column, GamebookParser, Grid, MissingPlaytimePercentage


gamekeys = (
    '56505',
)

gamekeys_percentage_pages = (
    ('56505', [17, 18], ),
    ('56918', [20, 21]),
)

def path_to_pdf(gamekey):
    return os.path.join(
        os.path.dirname(os.path.realpath(__file__)),
        'pdf',
        '{}.pdf'.format(gamekey))


def test_playtime_percentage_pages():
    for gamekey, percentage_pages in gamekeys_percentage_pages:
        with open(path_to_pdf(gamekey)) as pdf_file:
            pages = GamebookParser(pdf_file).playtime_percentage_pages(True)
            assert [page_num for page_num, _ in pages] == percentage_pages
            for _, layout in pages:
                assert isinstance(layout, LTPage)


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


def test_extract_playtime_percentage_56505():
    with open(path_to_pdf('56505')) as pdf_file:
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


def test_missing_data():
    with pytest.raises(MissingPlaytimePercentage):
        with open(path_to_pdf('56964')) as pdf_file:
            GamebookParser(pdf_file).extract_playtime_percentage()


def test_extract_playtime_percentage_56918():
    with open(path_to_pdf('56918')) as pdf_file:
        assert GamebookParser(pdf_file).extract_playtime_percentage() == (
            (u'San Francisco 49ers', [
                (u'J Staley', u'T', 65, 100, 0, 0, 5, 12),
                (u'Z Beadles', u'G', 65, 100, 0, 0, 5, 12),
                (u'T Brown', u'T', 65, 100, 0, 0, 5, 12),
                (u'B Gabbert', u'QB', 65, 100, 0, 0, 0, 0),
                (u'D Kilgore', u'C', 65, 100, 0, 0, 0, 0),
                (u'A Tiller', u'G', 61, 94, 0, 0, 5, 12),
                (u'Q Patton', u'WR', 57, 88, 0, 0, 7, 18),
                (u'T Smith', u'WR', 55, 85, 0, 0, 0, 0),
                (u'J Kerley', u'WR', 47, 72, 0, 0, 4, 10),
                (u'C Hyde', u'RB', 39, 60, 0, 0, 0, 0),
                (u'V McDonald', u'TE', 38, 58, 0, 0, 12, 30),
                (u'G Celek', u'TE', 32, 49, 0, 0, 8, 20),
                (u'S Draughn', u'RB', 22, 34, 0, 0, 15, 38),
                (u'R Streater', u'WR', 11, 17, 0, 0, 17, 42),
                (u'A Burbridge', u'WR', 10, 15, 0, 0, 16, 40),
                (u'B Bell', u'TE', 10, 15, 0, 0, 7, 18),
                (u'M Davis', u'RB', 4, 6, 0, 0, 13, 32),
                (u'M Martin', u'C', 4, 6, 0, 0, 0, 0),
                (u'E Reid', u'FS', 0, 0, 83, 100, 10, 25),
                (u'J Ward', u'CB', 0, 0, 83, 100, 10, 25),
                (u'N Bowman', u'LB', 0, 0, 83, 100, 10, 25),
                (u'T Brock', u'CB', 0, 0, 83, 100, 1, 2),
                (u'A Bethea', u'SS', 0, 0, 80, 96, 8, 20),
                (u'D Buckner', u'DT', 0, 0, 66, 80, 13, 32),
                (u'A Brooks', u'LB', 0, 0, 57, 69, 7, 18),
                (u'E Harold', u'LB', 0, 0, 57, 69, 4, 10),
                (u'G Hodges', u'LB', 0, 0, 56, 67, 7, 18),
                (u'Q Dial', u'DT', 0, 0, 48, 58, 15, 38),
                (u'M Purcell', u'NT', 0, 0, 46, 55, 17, 42),
                (u'A Armstead', u'DT', 0, 0, 41, 49, 7, 18),
                (u'R Armstrong', u'LB', 0, 0, 27, 33, 7, 18),
                (u'C Carradine', u'LB', 0, 0, 23, 28, 14, 35),
                (u'J Tartt', u'SS', 0, 0, 21, 25, 20, 50),
                (u'C Davis', u'CB', 0, 0, 15, 18, 10, 25),
                (u'G Dorsey', u'NT', 0, 0, 15, 18, 0, 0),
                (u'R Blair', u'DT', 0, 0, 11, 13, 10, 25),
                (u'R Robinson', u'CB', 0, 0, 11, 13, 9, 22),
                (u'K Reaser', u'CB', 0, 0, 7, 8, 8, 20),
                (u'D Johnson', u'CB', 0, 0, 0, 0, 34, 85),
                (u'M Wilhoite', u'LB', 0, 0, 0, 0, 34, 85),
                (u'N Bellore', u'LB', 0, 0, 0, 0, 25, 62),
                (u'K Nelson', u'LS', 0, 0, 0, 0, 12, 30),
                (u'B Pinion', u'P', 0, 0, 0, 0, 12, 30),
                (u'P Dawson', u'K', 0, 0, 0, 0, 11, 28),
                (u'J Garnett', u'G', 0, 0, 0, 0, 6, 15),
            ]),
            ('Carolina Panthers', [
                (u'M Oher', u'T', 83, 100, 0, 0, 9, 22),
                (u'A Norwell', u'G', 83, 100, 0, 0, 9, 22),
                (u'C Newton', u'QB', 83, 100, 0, 0, 0, 0),
                (u'R Kalil', u'C', 83, 100, 0, 0, 0, 0),
                (u'M Remmers', u'T', 82, 99, 0, 0, 9, 22),
                (u'T Turner', u'G', 77, 93, 0, 0, 8, 20),
                (u'G Olsen', u'TE', 76, 92, 0, 0, 0, 0),
                (u'D Funchess', u'WR', 55, 66, 0, 0, 0, 0),
                (u'K Benjamin', u'WR', 52, 63, 0, 0, 0, 0),
                (u'T Ginn', u'WR', 49, 59, 0, 0, 13, 32),
                (u'F Whittaker', u'RB', 49, 59, 0, 0, 8, 20),
                (u'C Brown', u'WR', 43, 52, 0, 0, 0, 0),
                (u'E Dickson', u'TE', 35, 42, 0, 0, 23, 58),
                (u'M Tolbert', u'FB', 29, 35, 0, 0, 6, 15),
                (u'D Williams', u'T', 11, 13, 0, 0, 9, 22),
                (u'J Stewart', u'RB', 10, 12, 0, 0, 0, 0),
                (u'S Simonson', u'TE', 7, 8, 0, 0, 1, 2),
                (u'B Bersin', u'WR', 5, 6, 0, 0, 15, 38),
                (u'D Hawkins', u'T', 1, 1, 0, 0, 9, 22),
                (u'J Bradberry', u'CB', 0, 0, 65, 100, 12, 30),
                (u'K Coleman', u'SS', 0, 0, 62, 95, 17, 42),
                (u'T Boston', u'FS', 0, 0, 62, 95, 17, 42),
                (u'L Kuechly', u'LB', 0, 0, 61, 94, 7, 18),
                (u'T Davis', u'LB', 0, 0, 61, 94, 5, 12),
                (u'B Benwikere', u'CB', 0, 0, 45, 69, 0, 0),
                (u'K Ealy', u'DE', 0, 0, 43, 66, 7, 18),
                (u'C Johnson', u'DE', 0, 0, 43, 66, 0, 0),
                (u'K Short', u'DT', 0, 0, 42, 65, 7, 18),
                (u'S Lotulelei', u'DT', 0, 0, 39, 60, 5, 12),
                (u'R McClain', u'CB', 0, 0, 31, 48, 7, 18),
                (u'V Butler', u'DT', 0, 0, 31, 48, 7, 18),
                (u'S Thompson', u'LB', 0, 0, 30, 46, 21, 52),
                (u'D Worley', u'CB', 0, 0, 28, 43, 26, 65),
                (u'M Addison', u'DE', 0, 0, 27, 42, 10, 25),
                (u'L Edwards', u'DE', 0, 0, 18, 28, 0, 0),
                (u'R Delaire', u'DE', 0, 0, 17, 26, 5, 12),
                (u'A Klein', u'LB', 0, 0, 4, 6, 24, 60),
                (u'C Jones', u'FS', 0, 0, 3, 5, 24, 60),
                (u'D Marlowe', u'SS', 0, 0, 3, 5, 13, 32),
                (u'D Mayo', u'LB', 0, 0, 0, 0, 24, 60),
                (u'J Cash', u'LB', 0, 0, 0, 0, 24, 60),
                (u'G Gano', u'K', 0, 0, 0, 0, 19, 48),
                (u'G Gradkowski', u'C', 0, 0, 0, 0, 15, 38),
                (u'J Jansen', u'LS', 0, 0, 0, 0, 12, 30),
                (u'A Lee', u'P', 0, 0, 0, 0, 12, 30),
            ]))
