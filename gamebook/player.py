from urllib import urlencode
import urllib2

from lxml import etree


class Player(object):

    @classmethod
    def gsis_id(cls, gamekey, short_name):
        pass

    @classmethod
    def full_name(cls, gamekey, short_name):
        parser = etree.XMLParser()
        url = 'http://www.nflgsis.com/2015/reg/01/56505/Gamebook.xml'
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
        return players[short_name.replace(' ', '.')]

    @classmethod
    def profile_url(cls, first_name, last_name):
        url = 'http://search.nfl.com/search?{}'.format(
            urlencode(dict(query=' '.join((first_name, last_name)))))
        parser = etree.HTMLParser()
        response = urllib2.urlopen(url)
        tree = etree.parse(response, parser)
        profile_url = tree.xpath('//a[@class="player"]/@href')[0]
        response.close()
        return profile_url
