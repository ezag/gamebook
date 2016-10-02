from gamebook.player import Player


def test_gsis_id():
    assert Player.gsis_id(gamekey, 'J Sitton') == '00-0026275'
    assert Player.gsis_id(gamekey, 'T Lang') == '00-0027078'
    assert Player.gsis_id(gamekey, 'B Bulaga') == '00-0027875'
    assert Player.gsis_id(gamekey, 'A Rodgers') == '00-0023459'
    assert Player.gsis_id(gamekey, 'D Bakhtiari') == '00-0030074'
    assert Player.gsis_id(gamekey, 'J Bushrod') == '00-0025512'
    assert Player.gsis_id(gamekey, 'M Slauson') == '00-0026500'
    assert Player.gsis_id(gamekey, 'V Ducasse') == '00-0027667'
    assert Player.gsis_id(gamekey, 'K Long') == '00-0030441'
    assert Player.gsis_id(gamekey, 'J Cutler') == '00-0024226'


def test_full_name():
    assert Player.full_name(gamekey, 'J Sitton') == ('Josh', 'Sitton')
    assert Player.full_name(gamekey, 'T Lang') == ('T.J.', 'Lang')
    assert Player.full_name(gamekey, 'B Bulaga') == ('Bryan', 'Bulaga')
    assert Player.full_name(gamekey, 'A Rodgers') == ('Aaron', 'Rodgers')
    assert Player.full_name(gamekey, 'D Bakhtiari') == ('David', 'Bakhtiari')
    assert Player.full_name(gamekey, 'J Bushrod') == ('Jermon', 'Bushrod')
    assert Player.full_name(gamekey, 'M Slauson') == ('Matt', 'Slauson')
    assert Player.full_name(gamekey, 'V Ducasse') == ('Vladimir', 'Ducasse')
    assert Player.full_name(gamekey, 'K Long') == ('Kyle', 'Long')
    assert Player.full_name(gamekey, 'J Cutler') == ('Jay', 'Cutler')


def test_profile_url():

    def url(slug, id_):
        return 'http://www.nfl.com/player/{}/{}/profile'.format(slug, id_)

    assert Player.profile_url('Josh', 'Sitton') == url('joshsitton', '4485')
    assert Player.profile_url('T.J.', 'Lang') == url('t.j.lang', '89746')
    assert Player.profile_url('Bryan', 'Bulaga') == url('bryanbulaga', '496988')
    assert Player.profile_url('Aaron', 'Rodgers') == url('aaronrodgers', '2506363')
    assert Player.profile_url('David', 'Bakhtiari') == url('davidbakhtiari', '2540183')
    assert Player.profile_url('Jermon', 'Bushrod') == url('jermonbushrod', '2507203')
    assert Player.profile_url('Matt', 'Slauson') == url('mattslauson' '81871')
    assert Player.profile_url('Vladimir', 'Ducasse') == url('vladimirducasse', '2508044')
    assert Player.profile_url('Kyle', 'Long') == url('kylelong', '2539933')
    assert Player.profile_url('Jay', 'Cutler') == url('jaycutler', '2495824')
