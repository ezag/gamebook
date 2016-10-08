from cStringIO import StringIO
import csv
import logging
import sys
import urllib2

from sqlalchemy import and_, or_
from sqlalchemy.engine import create_engine
from sqlalchemy.exc import IntegrityError
from sqlalchemy.sql import select

from .database import metadata, players, playtime_percentage
from .parse import GamebookParser, MissingPlaytimePercentage
from .player import Player


logging.basicConfig(
    stream=sys.stderr,
    level=logging.DEBUG,
    format='%(asctime)s %(levelname)s - %(message)s',
)
logger = logging.getLogger(__name__)

def parse_or_die(pdf):
    try:
        return GamebookParser(pdf).extract_playtime_percentage()
    except MissingPlaytimePercentage as exc:
        logging.critical(exc)
        sys.exit(1)


def pdf_to_csv():
    parsed = parse_or_die(sys.stdin)
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


def gsis_ids_with_cache(url, names_teams_positions, conn):
    uncached = []
    gsis_ids = {}
    for row in names_teams_positions:
        name, team, position = row
        result = conn.execute(select([players.c.gsis_id]).where(and_(
            players.c.name == name,
            players.c.team == team,
            players.c.position == position,
        ))).first()
        if result is None:
            uncached.append(row)
            continue
        gsis_id = result[0]
        gsis_ids[row] = gsis_id
        logger.info('Locally retrieved GSIS ID for %s: %s', name, gsis_id)
    uncached_gsis_ids = Player.gsis_ids(url, uncached)
    for row, gsis_id in zip(uncached, uncached_gsis_ids):
        if not gsis_id:
            continue
        name, team, position = row
        logger.info('Saving GSIS ID for %s locally', name)
        result = conn.execute(players.update().where(
            players.c.gsis_id == '00-0024226'
        ).values(
            name=name,
            team=team,
            position=position,
        ))
        if result.rowcount > 0:
            logger.warning('Overwrote existing record for GSIS ID %s', gsis_id)
        else:
            result = conn.execute(players.insert().values(
                gsis_id=gsis_id,
                name=name,
                team=team,
                position=position,
            ))
    gsis_ids.update(zip(uncached, uncached_gsis_ids))
    return [gsis_ids[row] for row in names_teams_positions]


def get_rows(url, game_id, conn=None):
    gamekey = url.rsplit('/', 2)[-2]
    response = urllib2.urlopen(url)
    pdf = StringIO(response.read())
    response.close()
    parsed = parse_or_die(pdf)
    for team in parsed:
        team_name, data = team
        player_names = [row.player_name for row in data]
        positions = [row.position for row in data]
        names_teams_positions = zip(
            player_names,
            [team_name] * len(player_names),
            positions,
        )
        players_gsis_ids = (
            gsis_ids_with_cache(url, names_teams_positions, conn)
            if conn is not None
            else Player.gsis_ids(url, names_teams_positions))
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
    for row in get_rows(url, game_id, conn):
        if not row['player_id']:
            row['player_id'] = None
        try:
            conn.execute(playtime_percentage.insert().values(**row))
        except IntegrityError as exc:
            result = conn.execute(playtime_percentage.delete().where(
                or_(
                    and_(
                        playtime_percentage.c.gamekey == row['gamekey'],
                        playtime_percentage.c.player_id == row['player_id'],
                    ),
                    and_(
                        playtime_percentage.c.gamekey == row['gamekey'],
                        playtime_percentage.c.player_name == row['player_name'],
                        playtime_percentage.c.team == row['team'],
                        playtime_percentage.c.position == row['position'],
                ))
            ))
            logger.warning(
                'Deleted %s row(s) for update %s',
                result.rowcount, row)
            conn.execute(playtime_percentage.insert().values(**row))


def create_table():
    engine = create_engine(sys.argv[1])
    metadata.create_all(engine)
