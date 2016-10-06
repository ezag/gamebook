from sqlalchemy.sql.schema import Column, MetaData, Table, UniqueConstraint
from sqlalchemy.sql.sqltypes import Integer, String


metadata = MetaData()

playtime_percentage = Table('playtime_percentage', metadata,
    Column('id', Integer, primary_key=True),
    Column('game_id', String),
    Column('gamekey', String),
    Column('player_id', String),
    Column('player_name', String),
    Column('position', String),
    Column('team', String),
    Column('off_snaps', Integer),
    Column('off_pct', Integer),
    Column('def_snaps', Integer),
    Column('def_pct', Integer),
    Column('spt_snaps', Integer),
    Column('spt_pct', Integer),
    UniqueConstraint('gamekey', 'player_name', 'team', 'position'),
    UniqueConstraint('gamekey', 'player_id'),
)
