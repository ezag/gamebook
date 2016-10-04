from urlparse import parse_qs, urlparse
import urllib2
import os.path

from gamebook.player import Player


def path_to_xml(gamekey):
    return os.path.join(
        os.path.dirname(os.path.realpath(__file__)),
        'xml',
        '{}.xml'.format(gamekey))


def path_to_search(name):
    return os.path.join(
        os.path.dirname(os.path.realpath(__file__)),
        'html',
        'search',
        '{}.html'.format(name.replace('.', '').replace(' ', '-').lower()))


def path_to_json(name):
    return os.path.join(
        os.path.dirname(os.path.realpath(__file__)),
        'json',
        '{}.json'.format(name))


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


def test_profile_url(monkeypatch):

    def url(slug, id_):
        return 'http://www.nfl.com/players/{}/profile?id={}'.format(slug, id_)

    def urlnew(slug, id_):
        return 'http://www.nfl.com/player/{}/{}/profile'.format(slug, id_)

    def mockreturn(url):
        parsed_url = urlparse(url)
        query = parse_qs(parsed_url.query)
        if 'query' in query:
            return open(path_to_search(query['query'][0]))
        elif 'q' in query:
            return open(path_to_json('vladimir-ducasse'))

    monkeypatch.setattr(urllib2, 'urlopen', mockreturn)

    assert Player.profile_url('Josh', 'Sitton') == url('JoshSitton', 'SIT702706')
    assert Player.profile_url('T.J.', 'Lang') == url('T.J.Lang', 'LAN483492')
    assert Player.profile_url('Bryan', 'Bulaga') == url('BryanBulaga', 'BUL062007')
    assert Player.profile_url('Aaron', 'Rodgers') == url('AaronRodgers', 'ROD339293')
    assert Player.profile_url('David', 'Bakhtiari') == url('DavidBakhtiari', 'BAK787653')
    assert Player.profile_url('Jermon', 'Bushrod') == url('JermonBushrod', 'BUS379552')
    assert Player.profile_url('Matt', 'Slauson') == url('MattSlauson', 'SLA733242')
    assert Player.profile_url('Vladimir', 'Ducasse') == urlnew('vladimirducasse', '2508044')
    assert Player.profile_url('Kyle', 'Long') == url('KyleLong', 'LON395646')
    assert Player.profile_url('Jay', 'Cutler') == url('JayCutler', 'CUT288111')
