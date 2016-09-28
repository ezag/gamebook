from gamebook.parse import ComponentType, GamebookParser


def assert_text_has_type(text, component_type):
    assert GamebookParser.type_from_text(text) == component_type


def test_team_name():
    assert_text_has_type(
        'Green Bay Packers\n',
        ComponentType.team_name)


def test_header():
    assert_text_has_type(
        'Offense\n',
        ComponentType.off_header)
    assert_text_has_type(
        'Defense Special Teams\n',
        ComponentType.def_spt_header)


def test_column_numeric():
    assert_text_has_type(
        '59\n59\n59\n59\n59\n59\n57\n54\n53\n45\n37\n23\n13\n7\n3\n1\n1\n1\n',
        ComponentType.numeric_column)
    assert_text_has_type(
        '5\n5\n5\n',
        ComponentType.numeric_column)
    assert_text_has_type(
        '1\n',
        ComponentType.numeric_column)
    assert_text_has_type(
        '8\n3\n6\n6\n5\n11\n9\n5\n14\n8\n6\n13\n6\n14\n1\n6\n6\n6\n11\n',
        ComponentType.numeric_column)
    assert_text_has_type(
        '15\n5\n21\n1\n',
        ComponentType.numeric_column)
    assert_text_has_type(
        '14\n14\n12\n11\n9\n7\n7\n5\n5\n',
        ComponentType.numeric_column)


def test_column_percentage():
    assert_text_has_type(
        '100%\n100%\n100%\n100%\n100%\n100%\n97%\n92%\n'
        '90%\n76%\n63%\n39%\n22%\n12%\n5%\n2%\n2%\n2%\n',
        ComponentType.percentage_column)
    assert_text_has_type(
        '19%\n19%\n19%\n',
        ComponentType.percentage_column)
    assert_text_has_type(
        '4%\n',
        ComponentType.percentage_column)
    assert_text_has_type(
        '31%\n12%\n23%\n23%\n19%\n42%\n35%\n19%\n54%\n31%\n'
        '23%\n50%\n23%\n54%\n4%\n23%\n23%\n23%\n42%\n',
        ComponentType.percentage_column)
    assert_text_has_type(
        '58%\n19%\n81%\n4%\n',
        ComponentType.percentage_column)
    assert_text_has_type(
        '54%\n54%\n46%\n42%\n35%\n27%\n27%\n19%\n19%\n',
        ComponentType.percentage_column)


def test_column_position():
    assert_text_has_type(
        'G\nG\nT\nQB\nT\nC\nWR\nWR\nWR\nRB\nTE\nTE\nRB\nFB\nG\nC\nWR\nWR\n'
        'FS\nFS\nLB\nCB\nCB\nLB\nCB\nDT\nLB\nLB\nNT\nLB\nSS\nNT\nLB\nLB\n'
        'DE\nDT\nLB\nSS\nFB\nK\nCB\nLS\nP\nT\nCB\n',
        ComponentType.position_column)


def test_column_dual():
    assert_text_has_type(
        '73 100%\n73 100%\n73 100%\n72 99%\n62 85%\n58 79%\n57 78%\n55 75%\n'
        '52 71%\n52 71%\n44 60%\n30 41%\n28 38%\n23 32%\n18 25%\n15 21%\n'
        '13 18%\n5\n7%\n',
        ComponentType.dual_column)


def test_column_player():
    assert_text_has_type(
        'J Sitton\nT Lang\nB Bulaga\nA Rodgers\nD Bakhtiari\nC Linsley\n'
        'D Adams\nJ Jones\nR Cobb\nE Lacy\nR Rodgers\nA Quarless\nJ Starks\n'
        'J Kuhn\nJ Walker\nJ Tretter\nJ Janis\nT Montgomery\nH Clinton-Dix\n'
        'M Hyde\nC Matthews\nS Shields\nC Hayward\nN Palmer\nD Randall\n'
        'M Daniels\nM Neal\nJ Peppers\nB Raji\nN Perry\nS Richardson\n'
        'J Boyd\nJ Elliott\nS Barrington\nM Pennel\nB Gaston\nJ Ryan\n'
        'C Banjo\nA Ripkowski\nM Crosby\nD Goodson\nB Goode\nT Masthay\n'
        'D Barclay\nQ Rollins\n',
        ComponentType.player_column)
