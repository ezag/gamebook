import csv
import sys

from .parse import GamebookParser


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
