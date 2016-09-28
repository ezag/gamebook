from gamebook.parse import ComponentType, GamebookParser


def assert_text_has_type(text, component_type):
    assert GamebookParser.type_from_text(text) == component_type


def test_team_name():
    assert_text_has_type('Green Bay Packers\n', ComponentType.team_name)
