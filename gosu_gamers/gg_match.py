"""
module for the retrieval of matches on http://www.gosugamers.com
"""
from urllib.parse import urljoin
import re

import requests
from lxml import html


# local
from gosu_gamers.match import Match

__author__ = 'rebsadran'


class MatchScraper:
    """
    Base class Match scrapers for gosugamers.com
    Override with url to <game>/gosubet.
    Override game with string of game name, used in match object
    """
    url = 'http://www.gosugamers.net/gosubet'
    domain = 'http://www.gosugamers.net/'
    game = None

    def __init__(self, fill=False):
        self.fill = fill

    def get_tree(self):
        """
        Downloads page and makes a html tree
        :return: HtmlElement tree
        """
        request = requests.get(self.url)
        tree = html.fromstring(request.content)
        return tree

    def find_all_matches(self):
        """Finds all matches (live, upcoming, recent)"""
        upcoming = self.find_upcoming_matches()
        live = self.find_live_matches()
        recent = self.find_recent_matches()
        return upcoming + live + recent

    def find_live_matches(self):
        """
        Finds live matches
        :returns list of Match objects
        """
        tree = self.get_tree()
        live_matches = tree.xpath('//*[self::h1 or self::h2][contains(text(),"Live")]/'
                                  'following-sibling::div[@class="content"]//tr')
        found = list(self._find_matches(live_matches))
        for m in found:
            m.live_in = 'Live'
        return found

    def find_upcoming_matches(self):
        """
        Finds upcoming matches
        :returns list of Match objects
        """
        tree = self.get_tree()
        upcoming_matches = tree.xpath('//*[self::h1 or self::h2][contains(text(),"Upcoming")]/'
                                      'following-sibling::div[@class="content"]//tr')
        return list(self._find_matches(upcoming_matches))

    def find_recent_matches(self):
        """
        Finds recent matches
        :returns list of Match objects
        """
        tree = self.get_tree()
        recent_matches = tree.xpath('//*[self::h1 or self::h2][contains(text(),"Recent")]/'
                                    'following-sibling::div[@class="content"]//tr')
        return list(self._find_matches(recent_matches))

    def _find_matches(self, match_trees):
        """
        Static method used by match finders to find matches from
        :param match_trees: list of html trees (usually table rows)
        """
        for match in match_trees:
            kwargs = {'team1': ''.join(match.xpath('.//span[contains(@class,"opp1")]//text()')).strip(),
                      'team2': ''.join(match.xpath('.//span[contains(@class,"opp2")]//text()')).strip(),
                      'team1_bet': ''.join(match.xpath('.//span[contains(@class,"bet1")]//text()')).strip('() \n'),
                      'team2_bet': ''.join(match.xpath('.//span[contains(@class,"bet2")]//text()')).strip('() \n'),
                      'live_in': ''.join(match.xpath('.//span[contains(@class,"live-in")]/text()')).strip(),
            }
            match_url = ''.join(match.xpath('.//a[contains(@class,"match")]/@href')).strip()
            match_id = re.findall('/matches/(\d+)', match_url)[0] if re.findall('/matches/(\d+)', match_url) else ''
            match_url = urljoin(self.domain, match_url)

            score = match.xpath('.//span[contains(@class,"score-wrap")]//span[contains(@class, "score")]/text()')
            kwargs['team1_score'] = score[0] if score else ''
            kwargs['team2_score'] = score[1] if len(score) > 1 else ''

            tournament = ''.join(match.xpath('.//a[contains(@class,"tournament")]/@href')).strip()
            kwargs['tournament'] = urljoin(self.domain, tournament)
            kwargs['has_vods'] = bool(match.xpath('.//span[contains(@class,"vod")]/img'))
            yield Match(match_id=match_id, url=match_url, fill=self.fill, **kwargs)


class CsGoMatchScraper(MatchScraper):
    url = 'http://www.gosugamers.net/counterstrike/gosubet'
    game = 'counterstrike'


class Dota2MatchScraper(MatchScraper):
    url = 'http://www.gosugamers.net/dota2/gosubet'
    game = 'dota2'


class LolMatchScraper(MatchScraper):
    url = 'http://www.gosugamers.net/lol/gosubet'
    game = 'league of legends'


class HearthStoneMatchScraper(MatchScraper):
    url = 'http://www.gosugamers.net/hearthstone/gosubet'
    game = 'hearthstone'


class HotsMatchScraper(MatchScraper):
    url = 'http://www.gosugamers.net/heroesofthestorm/gosubet'
    game = 'heroesofthestorm'


if __name__ == '__main__':
    ms = Dota2MatchScraper(fill=True)
    for game in ms.find_recent_matches():
        # game.fill_details()
        print(game)
        # print(game.team1_bet)