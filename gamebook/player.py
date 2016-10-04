from urllib import urlencode
import json
import urllib2

from lxml import etree


class Player(object):

    @classmethod
    def gsis_id(cls, game_url, short_name):
        full_name = cls.full_name(game_url, short_name)
        profile_url = cls.profile_url(*full_name)
        return cls.gsis_id_from_profile_url(profile_url)

    @classmethod
    def gsis_ids(cls, game_url, short_names):
        full_names = cls.full_names(game_url, short_names)
        profile_urls = [
            cls.profile_url(*full_name)
            for full_name in full_names]
        return [
            cls.gsis_id_from_profile_url(profile_url)
            for profile_url in profile_urls]

    @classmethod
    def gsis_id_from_profile_url(cls, profile_url):
        response = urllib2.urlopen(profile_url)
        parser = etree.HTMLParser()
        tree = etree.parse(response, parser)
        response.close()
        comment = tree.xpath('//comment()[contains(., "GSIS")]')[0].text
        gsis_id = [
            line.strip().split()[-1]
            for line in comment.split('\n')
            if line.strip().startswith('GSIS ID:')
        ][0]
        return gsis_id

    @classmethod
    def full_names(cls, game_url, short_names):
        parser = etree.XMLParser()
        url = '.'.join((game_url.rsplit('.', 1)[0], 'xml'))
        response = urllib2.urlopen(url)
        tree = etree.parse(response, parser)
        players = dict(
            (element.xpath('./@Player')[0], (
                element.xpath('./@NickName')[0],
                element.xpath('./@LastName')[0],
        )) for element in tree.xpath(
            '/Gamebook/GamebookSummary/*[{}]'.format('|'.join(
                'self::{}'.format(element) for element in (
                    'OffensiveStarterHome',
                    'DefensiveStarterHome',
                    'SubstitutionsHome',
                    'DidNotPlayHome',
                    'NotActiveHome',
                    'OffensiveStarterVisitor',
                    'DefensiveStarterVisitor',
                    'SubstitutionsVisitor',
                    'DidNotPlayVisitor',
                    'NotActiveVisitor',
        )))))
        response.close()
        return [
            players[short_name.replace(' ', '.')]
            for short_name in short_names
        ]

    @classmethod
    def full_name(cls, game_url, short_name):
        return cls.full_names(game_url, [short_name])[0]

    @classmethod
    def profile_url(cls, first_name, last_name):
        url = 'http://search.nfl.com/search?{}'.format(
            urlencode(dict(query=' '.join((first_name, last_name)))))
        parser = etree.HTMLParser()
        response = urllib2.urlopen(url)
        tree = etree.parse(response, parser)
        profile_url = tree.xpath('//a[@class="player"]/@href')
        if profile_url:
            assert len(profile_url) == 1
            profile_url = profile_url[0]
        else:
            profile_url = cls.profile_url_via_google(first_name, last_name)
        response.close()
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
        response = urllib2.urlopen(url)
        results = json.load(response)
        response.close()
        return results['items'][0]['link']
