from cStringIO import StringIO
import csv
import logging
import sys
import urllib2

from sqlalchemy.engine import create_engine
from sqlalchemy.exc import IntegrityError

from .database import metadata, playtime_percentage
from .parse import GamebookParser
from .player import Player


logging.basicConfig(
    stream=sys.stderr,
    level=logging.DEBUG,
    format='%(asctime)s %(levelname)s - %(message)s',
)
logger = logging.getLogger(__name__)

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


field_names = (
    'game_id',
    'gamekey',
    'player_id',
    'player_name',
    'position',
    'team',
    'off_snaps',
    'off_pct',
    'def_snaps',
    'def_pct',
    'spt_snaps',
    'spt_pct',
)


def get_rows(url, game_id):
    gamekey = url.rsplit('/', 2)[-2]
    response = urllib2.urlopen(url)
    pdf = StringIO(response.read())
    response.close()
    gb = GamebookParser(pdf)
    parsed = gb.extract_playtime_percentage()
    for team in parsed:
        team_name, data = team
        player_names = [row.player_name for row in data]
        players_gsis_ids = Player.gsis_ids(url, player_names)
        for row, gsis_id in zip(data, players_gsis_ids):
            yield dict(zip(field_names, (
                game_id,
                gamekey,
                gsis_id,
                row.player_name,
                row.position,
                team_name,
                row.off_snaps,
                row.off_pct,
                row.def_snaps,
                row.def_pct,
                row.spt_snaps,
                row.spt_pct,
            )))


def url_to_csv():
    url = sys.argv[1]
    game_id = sys.argv[2]
    out = csv.writer(sys.stdout)
    out.writerow(field_names)
    for row in get_rows(url, game_id):
        out.writerow([row[key] for key in field_names])


def url_to_db():
    url = sys.argv[1]
    game_id = sys.argv[2]
    db_uri = sys.argv[3]
    engine = create_engine(db_uri)
    conn = engine.connect()
    for row in get_rows(url, game_id):
        if not row['player_id']:
            row['player_id'] = None
        try:
            conn.execute(playtime_percentage.insert().values(**row))
        except IntegrityError as exc:
            logger.warning('Ignoring new record %s\n%s', exc.params, exc)


def create_table():
    engine = create_engine(sys.argv[1])
    metadata.create_all(engine)
