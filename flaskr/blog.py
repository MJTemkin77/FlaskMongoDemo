from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)

from werkzeug.exceptions import abort

from flaskr.auth import login_required
from flaskr.db import get_db

from sqlalchemy import text, insert, select, delete as sa_delete, update as sa_update
from sqlalchemy.exc import IntegrityError
from .db import get_db, user, post

bp = Blueprint('blog', __name__)

def getPostExpr(id=None):
    '''
     (db.execute(
     text('select p.id, title, body, created, author_id, username '
                    ' FROM post p JOIN user u ON p.author_id = u.id '
                    ' ORDER BY created DESC'))

    Change to SQLAlchemy Core expression
     '''
    if id is None:
        return (
            select(post.c.id, post.c.title, post.c.body, post.c.created,
                   post.c.author_id, user.c.username)
            .select_from(post.join(user, post.c.author_id == user.c.id))
            .order_by(post.c.created.desc())
        )
    else:
        return (
            select(post.c.id, post.c.title, post.c.body, post.c.created,
                   post.c.author_id, user.c.username)
            .select_from(post.join(user, post.c.author_id == user.c.id))
            .where(post.c.id == id)
            .order_by(post.c.created.desc())
        )



@bp.route('/')
def index():
    db = get_db()
    posts = db.execute(getPostExpr()).mappings().all()


    return render_template('blog/index.html', posts=posts)


@bp.route('/create', methods=('GET', 'POST'))
@login_required
def create():
    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        error = None

        if not title:
            error = 'Title is required.'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(insert(post).values(title=title, body=body, author_id =g.user['id']))
            db.commit()
            return redirect(url_for('blog.index'))

    return render_template('blog/create.html')


def get_post(id, check_author=True):
    post = get_db().execute(getPostExpr(id)).mappings().first()

    if post is None:
        abort(404,f'Post with id {id} not found')

    if check_author and post['author_id'] != g.user['id']:
        abort(403)

    return post

@bp.route('/<int:id>/update', methods=('GET', 'POST'))
@login_required
def update(id):
    updt_post = get_post(id)

    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        error = None

        if not title:
            error = 'Title is required.'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(sa_update(post).where(post.c.id == id).values(title=title, body=body))
            db.commit()
            return redirect(url_for('blog.index'))

    return render_template('blog/update.html', post=updt_post)

@bp.route('/<int:id>/delete', methods=('POST',))
@login_required
def delete(id):
    db = get_db()
    db.execute(sa_delete(post).where(post.c.id == id))
    db.commit()
    return redirect(url_for('blog.index'))



