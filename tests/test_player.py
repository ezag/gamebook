from urlparse import parse_qs, urlparse
import urllib2
import os.path

from gamebook.player import Player


def path_to_xml(game_url):
    return os.path.join(
        os.path.dirname(os.path.realpath(__file__)),
        'xml',
        '{}.xml'.format(game_url))


def path_to_search(name):
    return os.path.join(
        os.path.dirname(os.path.realpath(__file__)),
        'html',
        'search',
        '{}.html'.format(name.replace('.', '').replace(' ', '-').lower()))


def path_to_profile(name):
    return os.path.join(
        os.path.dirname(os.path.realpath(__file__)),
        'html',
        'profile',
        '{}.html'.format(name))


def path_to_json(name):
    return os.path.join(
        os.path.dirname(os.path.realpath(__file__)),
        'json',
        '{}.json'.format(name))


def mock_urlopen(url):
    if url.endswith('xml'):
        filename = path_to_xml('56505')
    elif url.startswith('https://www.googleapis.com/'):
        filename = path_to_json('vladimir-ducasse')
    elif url.startswith('http://search.nfl.com/'):
        parsed_url = urlparse(url)
        query = parse_qs(parsed_url.query)
        filename = path_to_search(query['query'][0])
    elif url.startswith('http://www.nfl.com/'):
        name = url.split('/')[4].lower().replace('.', '')
        filename = path_to_profile(name)
    else:
        assert False
    return open(filename)


def test_gsis_id(monkeypatch):
    monkeypatch.setattr(urllib2, 'urlopen', mock_urlopen)
    game_url = 'http://www.nflgsis.com/2015/reg/01/56505/Gamebook.pdf'
    assert Player.gsis_id(game_url, 'J Sitton') == '00-0026275'
    assert Player.gsis_id(game_url, 'T Lang') == '00-0027078'
    assert Player.gsis_id(game_url, 'B Bulaga') == '00-0027875'
    assert Player.gsis_id(game_url, 'A Rodgers') == '00-0023459'
    assert Player.gsis_id(game_url, 'D Bakhtiari') == '00-0030074'
    assert Player.gsis_id(game_url, 'J Bushrod') == '00-0025512'
    assert Player.gsis_id(game_url, 'M Slauson') == '00-0026500'
    assert Player.gsis_id(game_url, 'V Ducasse') == '00-0027667'
    assert Player.gsis_id(game_url, 'K Long') == '00-0030441'
    assert Player.gsis_id(game_url, 'J Cutler') == '00-0024226'


def test_full_name(monkeypatch):
    monkeypatch.setattr(urllib2, 'urlopen', mock_urlopen)
    game_url = 'http://www.nflgsis.com/2015/reg/01/56505/Gamebook.pdf'
    assert Player.full_name(game_url, 'J Sitton') == ('Josh', 'Sitton')
    assert Player.full_name(game_url, 'T Lang') == ('T.J.', 'Lang')
    assert Player.full_name(game_url, 'B Bulaga') == ('Bryan', 'Bulaga')
    assert Player.full_name(game_url, 'A Rodgers') == ('Aaron', 'Rodgers')
    assert Player.full_name(game_url, 'D Bakhtiari') == ('David', 'Bakhtiari')
    assert Player.full_name(game_url, 'J Bushrod') == ('Jermon', 'Bushrod')
    assert Player.full_name(game_url, 'M Slauson') == ('Matt', 'Slauson')
    assert Player.full_name(game_url, 'V Ducasse') == ('Vladimir', 'Ducasse')
    assert Player.full_name(game_url, 'K Long') == ('Kyle', 'Long')
    assert Player.full_name(game_url, 'J Cutler') == ('Jay', 'Cutler')


def test_profile_url(monkeypatch):

    def url(slug, id_):
        return 'http://www.nfl.com/players/{}/profile?id={}'.format(slug, id_)

    def urlnew(slug, id_):
        return 'http://www.nfl.com/player/{}/{}/profile'.format(slug, id_)

    monkeypatch.setattr(urllib2, 'urlopen', mock_urlopen)
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
