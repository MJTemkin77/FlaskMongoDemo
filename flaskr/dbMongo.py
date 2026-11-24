from datetime import datetime

import click
from flask import current_app, g

from pymongo import MongoClient


class user(object):
    def __init__(self, username, password):
        self.username = username
        self.password = password
        self.id = ""

class post(object):
    def __init__(self, postauthor:user, created:datetime, title:str, body:str):
        self.postauthor = postauthor
        self.created = created
        self.title = title
        self.body = body
        self.id = ""


def get_engine():
    return current_app.extensions['db_engine']

def get_db():
    """One Connection per request, stored on g."""
    if 'db' not in g:
        g.db = get_engine().connect()
    return g.db


def close_db(e=None):
    db = g.pop('db', None)
    if db is not None:
        db.close()

def init_db():
    engine = get_engine()
    #metadata.drop_all(engine)
    #metadata.create_all(engine)


def init_app(app):
    app.extensions['db_engine'] = (
        MongoClient(
            app.config['MONGO_SERVER'], app.config['MONGO_PORT'])
    )
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)



@click.command('init-db')
def init_db_command():
    """Clear the existing data and create new tables."""
    init_db()
    click.echo('Initialized the database.')

