from cStringIO import StringIO
import csv
import sys
import urllib2

from .parse import GamebookParser
from .player import Player


def pdf_to_csv():
    gb = GamebookParser(sys.stdin)
    parsed = gb.extract_playtime_percentage()
    out = csv.writer(sys.stdout)
    out.writerow((
        'team_name',
        'player_name',
        'position',
        'off_snaps',
        'off_pct',
        'def_snaps',
        'def_pct',
        'spt_snaps',
        'spt_pct',
    ))
    for team in parsed:
        team_name, data = team
        for row in data:
            csvrow = [team_name]
            csvrow.extend(row)
            out.writerow(csvrow)


def url_to_csv():
    url = sys.argv[1]
    response = urllib2.urlopen(url)
    pdf = StringIO(response.read())
    response.close()
    gb = GamebookParser(pdf)
    parsed = gb.extract_playtime_percentage()
    out = csv.writer(sys.stdout)
    out.writerow((
        'team_name',
        'player_id',
        'player_name',
        'position',
        'off_snaps',
        'off_pct',
        'def_snaps',
        'def_pct',
        'spt_snaps',
        'spt_pct',
    ))
    for team in parsed:
        team_name, data = team
        player_names = [row.player_name for row in data]
        players_gsis_ids = Player.gsis_ids(url, player_names)
        for row, gsis_id in zip(data, players_gsis_ids):
            print type(row)
            csvrow = (
                team_name,
                gsis_id,
                row.player_name,
                row.position,
                row.off_snaps,
                row.off_pct,
                row.def_snaps,
                row.def_pct,
                row.spt_snaps,
                row.spt_pct,
            )
            out.writerow(csvrow)
