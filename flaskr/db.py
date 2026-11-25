from datetime import datetime

import click
from flask import current_app, g

from sqlalchemy import (
    create_engine, MetaData, Table, Column,
    Integer, String, Text, DateTime, ForeignKey, func,
)

metadata = MetaData()

# Replaces schema.sql (the Flask tutorial's tables, as an example)
user = Table(
    'user', metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('username', String(255), unique=True, nullable=False),
    Column('password', String(255), nullable=False),
)

post = Table(
    'post', metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('author_id', Integer, ForeignKey('user.id'), nullable=False),
    Column('created', DateTime, nullable=False, server_default=func.now()),
    Column('title', String(255), nullable=False),
    Column('body', Text, nullable=False),
)


def get_engine():
    return current_app.extensions['db_engine']

def get_db():
    """One Connection per request, stored on g."""
    if 'db' not in g:
        g.db = get_engine().connect()
    return g.db


def close_db(e=None):
   pass
   '''
    db = g.pop('db', None)
    if db is not None:
        db.close()
    '''
def init_db():
    engine = get_engine()
    metadata.drop_all(engine)
    metadata.create_all(engine)


def init_app(app):
    app.extensions['db_engine'] = create_engine(
        app.config['DATABASE_URL'],
        pool_pre_ping=True,   # survive MariaDB dropping idle connections
        pool_recycle=3600,
    )
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)



@click.command('init-db')
def init_db_command():
    """Clear the existing data and create new tables."""
    init_db()
    click.echo('Initialized the database.')

