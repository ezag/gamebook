import urllib2
import os.path

from gamebook.player import Player


def path_to_xml(gamekey):
    return os.path.join(
        os.path.dirname(os.path.realpath(__file__)),
        'xml',
        '{}.xml'.format(gamekey))


def test_gsis_id():
    assert Player.gsis_id('56505', 'J Sitton') == '00-0026275'
    assert Player.gsis_id('56505', 'T Lang') == '00-0027078'
    assert Player.gsis_id('56505', 'B Bulaga') == '00-0027875'
    assert Player.gsis_id('56505', 'A Rodgers') == '00-0023459'
    assert Player.gsis_id('56505', 'D Bakhtiari') == '00-0030074'
    assert Player.gsis_id('56505', 'J Bushrod') == '00-0025512'
    assert Player.gsis_id('56505', 'M Slauson') == '00-0026500'
    assert Player.gsis_id('56505', 'V Ducasse') == '00-0027667'
    assert Player.gsis_id('56505', 'K Long') == '00-0030441'
    assert Player.gsis_id('56505', 'J Cutler') == '00-0024226'


def test_full_name(monkeypatch):

    def mockreturn(url):
        return open(path_to_xml('56505'))

    monkeypatch.setattr(urllib2, 'urlopen', mockreturn)

    assert Player.full_name('56505', 'J Sitton') == ('Josh', 'Sitton')
    assert Player.full_name('56505', 'T Lang') == ('T.J.', 'Lang')
    assert Player.full_name('56505', 'B Bulaga') == ('Bryan', 'Bulaga')
    assert Player.full_name('56505', 'A Rodgers') == ('Aaron', 'Rodgers')
    assert Player.full_name('56505', 'D Bakhtiari') == ('David', 'Bakhtiari')
    assert Player.full_name('56505', 'J Bushrod') == ('Jermon', 'Bushrod')
    assert Player.full_name('56505', 'M Slauson') == ('Matt', 'Slauson')
    assert Player.full_name('56505', 'V Ducasse') == ('Vladimir', 'Ducasse')
    assert Player.full_name('56505', 'K Long') == ('Kyle', 'Long')
    assert Player.full_name('56505', 'J Cutler') == ('Jay', 'Cutler')


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
