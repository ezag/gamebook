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


def mock_urlopen(url, **kwargs):
    if url.endswith('xml'):
        name = url.rsplit('/', 2)[-2]
        filename = path_to_xml(name)
    elif url.startswith('https://www.googleapis.com/'):
        parsed_url = urlparse(url)
        query = parse_qs(parsed_url.query)
        search_string = query['q'][0]
        name = search_string.split(' ')[0].split(':')[1]
        filename = path_to_json(name)
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
    assert Player.gsis_id(game_url, 'J Sitton', 'Green Bay Packers', 'G') == '00-0026275'
    assert Player.gsis_id(game_url, 'T Lang', 'Green Bay Packers', 'G') == '00-0027078'
    assert Player.gsis_id(game_url, 'B Bulaga', 'Green Bay Packers', 'T') == '00-0027875'
    assert Player.gsis_id(game_url, 'A Rodgers', 'Green Bay Packers', 'QB') == '00-0023459'
    assert Player.gsis_id(game_url, 'D Bakhtiari', 'Green Bay Packers', 'T') == '00-0030074'
    assert Player.gsis_id(game_url, 'J Bushrod', 'Chicago Bears', 'T') == '00-0025512'
    assert Player.gsis_id(game_url, 'M Slauson', 'Chicago Bears', 'G') == '00-0026500'
    assert Player.gsis_id(game_url, 'V Ducasse', 'Chicago Bears', 'G') == '00-0027667'
    assert Player.gsis_id(game_url, 'K Long', 'Chicago Bears', 'G') == '00-0030441'
    assert Player.gsis_id(game_url, 'J Cutler', 'Chicago Bears', 'QB') == '00-0024226'


def test_full_name(monkeypatch):
    monkeypatch.setattr(urllib2, 'urlopen', mock_urlopen)
    game_url = 'http://www.nflgsis.com/2015/reg/01/56505/Gamebook.pdf'
    assert Player.full_name(game_url, 'J Sitton', 'Green Bay Packers', 'G') == ('Josh', 'Sitton')
    assert Player.full_name(game_url, 'T Lang', 'Green Bay Packers', 'G') == ('T.J.', 'Lang')
    assert Player.full_name(game_url, 'B Bulaga', 'Green Bay Packers', 'T') == ('Bryan', 'Bulaga')
    assert Player.full_name(game_url, 'A Rodgers', 'Green Bay Packers', 'QB') == ('Aaron', 'Rodgers')
    assert Player.full_name(game_url, 'D Bakhtiari', 'Green Bay Packers', 'T') == ('David', 'Bakhtiari')
    assert Player.full_name(game_url, 'J Bushrod', 'Chicago Bears', 'T') == ('Jermon', 'Bushrod')
    assert Player.full_name(game_url, 'M Slauson', 'Chicago Bears', 'G') == ('Matt', 'Slauson')
    assert Player.full_name(game_url, 'V Ducasse', 'Chicago Bears', 'G') == ('Vladimir', 'Ducasse')
    assert Player.full_name(game_url, 'K Long', 'Chicago Bears', 'G') == ('Kyle', 'Long')
    assert Player.full_name(game_url, 'J Cutler', 'Chicago Bears', 'QB') == ('Jay', 'Cutler')


def test_full_name_multispace(monkeypatch):
    monkeypatch.setattr(urllib2, 'urlopen', mock_urlopen)
    game_url = 'http://www.nflgsis.com/2016/REG/04/56953/Gamebook.pdf'
    assert Player.full_name(game_url, 'K Van Noy', 'Detroit Lions', 'LB') == ('Kyle', 'Van Noy')


def test_full_name_from_ambiguous(monkeypatch):
    monkeypatch.setattr(urllib2, 'urlopen', mock_urlopen)
    game_url = 'http://www.nflgsis.com/2016/REG/04/56952/Gamebook.pdf'
    assert Player.full_name(game_url, 'S Smith', 'Oakland Raiders', 'CB') == ('Sean', 'Smith')
    assert Player.full_name(game_url, 'S Smith', 'Baltimore Ravens', 'WR') == ('Steve', 'Smith')


def test_full_name_from_ambiguous_same_team(monkeypatch):
    monkeypatch.setattr(urllib2, 'urlopen', mock_urlopen)
    game_url = 'http://www.nflgsis.com/2016/reg/01/56902/Gamebook.pdf'
    assert Player.full_name(game_url, 'D Smith', 'Tampa Bay Buccaneers', 'LB') == ('Daryl', 'Smith')
    assert Player.full_name(game_url, 'D Smith', 'Tampa Bay Buccaneers', 'T') == ('Donovan', 'Smith')
    game_url = 'http://www.nflgsis.com/2016/reg/04/56956/Gamebook.pdf'
    assert Player.full_name(game_url, 'J Jenkins', 'New York Jets', 'LB') == ('Jordan', 'Jenkins')
    assert Player.full_name(game_url, 'J Jenkins', 'New York Jets', 'DE') == ('Jarvis', 'Jenkins')


def test_full_name_indistinguishable(monkeypatch):
    monkeypatch.setattr(urllib2, 'urlopen', mock_urlopen)
    game_url = 'http://www.nflgsis.com/2016/reg/01/56914/Gamebook.pdf'
    full_name_1 = Player.full_name(game_url, 'J Brown', 'Arizona Cardinals', 'WR')
    full_name_2 = Player.full_name(game_url, 'J Brown', 'Arizona Cardinals', 'WR')
    assert full_name_1 != full_name_2


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


def test_profile_url_ambiguous(monkeypatch):

    def urlnew(slug, id_):
        return 'http://www.nfl.com/player/{}/{}/profile'.format(slug, id_)

    monkeypatch.setattr(urllib2, 'urlopen', mock_urlopen)
    assert Player.profile_url('Don', 'Jones') == urlnew('donjones', '2541154')


def test_broken_profile(monkeypatch):
    monkeypatch.setattr(urllib2, 'urlopen', mock_urlopen)
    assert Player.profile_url('Non', 'Existent') is None


def test_broken_full_name(monkeypatch):
    monkeypatch.setattr(urllib2, 'urlopen', mock_urlopen)
    game_url = 'http://www.nflgsis.com/2015/reg/01/56505/Gamebook.pdf'
    assert Player.full_name(game_url, 'N Existent', 'Green Bay Packers', 'G') == None
    assert Player.gsis_id(game_url, 'N Existent', 'Green Bay Packers', 'G') == ''
    assert Player.gsis_ids(game_url, [
        ('N Existent', 'Green Bay Packers', 'G'),
        ('J Sitton', 'Green Bay Packers', 'G'),
    ]) == [
        '',
        '00-0026275',
    ]


def test_broken_gsis_id(monkeypatch):
    monkeypatch.setattr(urllib2, 'urlopen', mock_urlopen)
    url = 'http://www.nfl.com/player/brokengsis/test/profile' 
    assert Player.gsis_id_from_profile_url(url) == ''
