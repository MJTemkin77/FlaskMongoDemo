import functools
from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.security import generate_password_hash, check_password_hash

from flaskr.db import get_db

from .dbMongo import get_db, user, post
from bson import ObjectId

from pymongo import MongoClient

bp = Blueprint('auth', __name__, url_prefix='/auth')


@bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db= get_db()
        error = None

        if not username:
            error = 'Username is required.'
        elif not password:
            error = 'Password is required.'

        if error is None:
            try:
                db = get_db()
                db.users.insert_one({'username': username, 'password': generate_password_hash(password)})
                #db.execute(insert(user).values(username=username, password=generate_password_hash(password)))
                #db.commit()
            except db.IntegrityError:
                error = f"User {username} already is already registered."
            else:
                return redirect(url_for('auth.login'))

        flash(error)
    return render_template('auth/register.html')

@bp.route('/login', methods=['GET', 'POST'])
def login():
    #breakpoint()
    print("login() reached", __file__)
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db= get_db()
        error = None

        row = db.users.find_one({'username': username})
        #row = db.execute(select(user).where(user.c.username == username)).mappings().first()
        print(row)
        if row is None:
            error = 'Incorrect username.'
        elif not check_password_hash(row['password'], password):
            error = 'Incorrect password.'

        if error is None:
            session.clear()
            session['user_id'] = str(row['_id'])
            return redirect(url_for('index'))

        flash(error)

    return render_template('auth/login.html')

@bp.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')
    if user_id is None:
        g.user = None
    else:
        #g.user = get_db().execute(select(user).where(user.c.id == user_id)).mappings().first()
        g.user = get_db().users.find_one({'_id':ObjectId(user_id)})

@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('auth.index'))


def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))
        return view(**kwargs)
    return wrapped_view

@bp.route("/")
def index():
    """Show all the posts, most recent first."""
    db = get_db()
    return "Hi from Index"

