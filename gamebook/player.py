from urllib import urlencode
import json
import logging
import urllib2

from lxml import etree


logger = logging.getLogger(__name__)

class Player(object):

    @classmethod
    def gsis_id(cls, game_url, short_name, team_name, position):
        full_name = cls.full_name(game_url, short_name, team_name, position)
        if full_name is None:
            return ''
        profile_url = cls.profile_url(*full_name)
        return cls.gsis_id_from_profile_url(profile_url)

    @classmethod
    def gsis_ids(cls, game_url, names_teams_positions):
        full_names = cls.full_names(game_url, names_teams_positions)
        profile_urls = [
            cls.profile_url(*full_name) if full_name is not None else None
            for full_name in full_names]
        return [
            cls.gsis_id_from_profile_url(profile_url)
            for profile_url in profile_urls]

    @classmethod
    def gsis_id_from_profile_url(cls, profile_url):
        if profile_url is None:
            return ''
        logger.info('GSIS ID from %s...', profile_url)
        try:
            tree = cls.get_html(profile_url)
        except Exception:
            logger.exception('Failed to get GSIS ID from %s', profile_url)
            return ''
        comment = tree.xpath('//comment()[contains(., "GSIS")]')
        if not comment:
            logger.warning('Missing GSIS ID at %s', profile_url)
            return ''
        comment = comment[0].text
        gsis_id = [
            line.strip().split()[-1]
            for line in comment.split('\n')
            if line.strip().startswith('GSIS ID:')
        ][0]
        logger.info('...found: %s', gsis_id)
        return gsis_id

    @classmethod
    def full_names(cls, game_url, names_teams_positions):

        def players_from_tree(tree, suffix):
            return  dict(
                (element.xpath('./@Player')[0], (
                    element.xpath('./@NickName')[0],
                    element.xpath('./@LastName')[0],
            )) for element in tree.xpath(
                '/Gamebook/GamebookSummary/*[{}]'.format('|'.join(
                    'self::{}{}'.format(element, suffix) for element in (
                        'OffensiveStarter',
                        'DefensiveStarter',
                        'Substitutions',
                        'DidNotPlay',
                        'NotActive',
            )))))

        url = '.'.join((game_url.rsplit('.', 1)[0], 'xml'))
        tree = cls.get_xml(url)
        home_players = players_from_tree(tree, 'Home')
        visitor_players = players_from_tree(tree, 'Visitor')
        home_team = tree.xpath('/Gamebook/GamebookSummary/@HomeTeam')[0]
        visitor_team = tree.xpath('/Gamebook/GamebookSummary/@VisitingTeam')[0]
        players = {home_team: home_players, visitor_team: visitor_players}
        full_names = []
        for short_name, team_name, position in names_teams_positions:
            full_name = players[team_name].get(short_name.replace(' ', '.', 1))
            if full_name is None:
                logger.warning(
                    'Missing full name for %s at %s',
                    short_name, url)
            full_names.append(full_name)
        return full_names

    @classmethod
    def full_name(cls, game_url, short_name, team_name, position):
        return cls.full_names(game_url, [(short_name, team_name, position)])[0]

    @classmethod
    def profile_url(cls, first_name, last_name):
        logger.info('Profile URL for %s %s...', first_name, last_name)
        url = 'http://search.nfl.com/search?{}'.format(
            urlencode(dict(query=' '.join((first_name, last_name)))))
        try:
            tree = cls.get_html(url)
        except Exception:
            logger.exception(
                'Failed to get profile URL for %s %s from %s',
                first_name, last_name, url)
            return None
        profile_url = tree.xpath('//a[@class="player"]/@href')
        if profile_url:
            if len(profile_url) > 1:
                logger.warning(
                    'Ignoring extra profile URLs for %s %s at %s',
                    first_name, last_name, url)
            profile_url = profile_url[0]
        else:
            logger.info('...falling back to Google...')
            profile_url = cls.profile_url_via_google(first_name, last_name)
        logger.info('...found: %s', profile_url)
        return profile_url

    @classmethod
    def profile_url_via_google(cls, first_name, last_name):
        # http://stackoverflow.com/a/11206266/443594
        url = 'https://www.googleapis.com/customsearch/v1?{}'.format(urlencode(dict(
            key='AIzaSyDdz3sni-hy81oqHN38-NNdvyc9E8GOTRk',
            cx='008652676468622773486:v3ihrvnf_xi',
            q='inurl:{}{} inurl:profile'.format(
                first_name.lower(),
                last_name.lower(),
            ),
        )))
        try:
            results = cls.get_json(url)
        except Exception:
            logger.exception(
                'Failed to get profile URL for %s %s from %s',
                first_name, last_name, url)
            return None
        if 'items' not in results or not results['items']:
            logger.warning('Missing profile for %s %s', first_name, last_name)
            return None
        if len(results['items']) > 1:
            logger.warning(
                'Ignoring extra profile URLs for %s %s at %s',
                first_name, last_name, url)
        return results['items'][0]['link']

    @classmethod
    def get_tree(cls, url, parser):
        response = cls.urlopen_with_retry(url)
        tree = etree.parse(response, parser)
        response.close()
        return tree

    @classmethod
    def get_html(cls, url):
        return cls.get_tree(url, etree.HTMLParser())

    @classmethod
    def get_xml(cls, url):
        return cls.get_tree(url, etree.XMLParser())

    @classmethod
    def get_json(cls, url):
        response = cls.urlopen_with_retry(url)
        data = json.load(response)
        response.close()
        return data

    @classmethod
    def urlopen_with_retry(cls, url, retries=3, delay_sec=5):
        try:
            return urllib2.urlopen(url)
        except urllib2.URLError as exc:
            logger.warning('Failed accessing URL %s - %s', url, exc.reason)
            if retries > 0:
                logger.info('Retry in %s seconds', delay_sec)
                return cls.urlopen_with_retry(url, retries - 1, delay_sec + 5)
            else:
                logger.info('No more retries')
                raise
