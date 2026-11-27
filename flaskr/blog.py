from datetime import datetime

from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)

from werkzeug.exceptions import abort

from flaskr.auth import login_required

from bson import ObjectId

from sqlalchemy import text, insert, select, delete as sa_delete, update as sa_update
from sqlalchemy.exc import IntegrityError
from .dbMongo import get_db, user, post


bp = Blueprint('blog', __name__)

def getPostExpr(id=None):
    '''
     (db.execute(
     text('select p.id, title, body, created, author_id, username '
                    ' FROM post p JOIN user u ON p.author_id = u.id '
                    ' ORDER BY created DESC'))

    Change to SQLAlchemy Core expression
     '''
    findExpr = {"_id":id}
    if (id is None):
        findExpr = {}
    projectExpr = {"_id":1, "title":1, "body":1, "created":1, "BlogAuthor":1}
    orderExpr = {"created":-1}
    return findExpr, projectExpr, orderExpr



@bp.route('/')
def index():
    db = get_db()
    findExpr, projectExpr, orderExpr = getPostExpr()
    posts = db.posts.find(findExpr, projectExpr).sort(orderExpr).to_list()


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
            userDoc = db.users.find_one({'_id': g.user['_id']})
            db.posts.insert_one({'title': title, 'body': body,'created' : datetime.now(), 'BlogAuthor': {'Name':userDoc['username'], 'Id':userDoc['_id'] }})
            return redirect(url_for('blog.index'))

    return render_template('blog/create.html')


def get_post(id, check_author=True):
    db = get_db()
    findExpr, projectExpr, _ = getPostExpr(id)
    post = db.posts.find_one(findExpr, projectExpr)

    if post is None:
        abort(404,f'Post with id {id} not found')

    if check_author and post['BlogAuthor']['Id'] != g.user['_id']:
        abort(403)

    return post

@bp.route('/<string:id>/update', methods=('GET', 'POST'))
@login_required
def update(id):
    # The reason to store the ObjectId of id to a variable
    # is so that you can step into the get_post function without having
    # to step through the ObjectId function code.
    oid = ObjectId(id)
    updt_post = get_post(oid)

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
            db.posts.update_one({'_id': oid}, {'$set': {'title': title, 'body': body}})
            return redirect(url_for('blog.index'))

    return render_template('blog/update.html', post=updt_post)

@bp.route('/<string:id>/delete', methods=('POST',))
@login_required
def delete(id):
    db = get_db()
    # The reason to store the ObjectId of id to a variable
    # is so that you can step into the get_post function without having
    # to step through the ObjectId function code.
    oid = ObjectId(id)
    db.posts.delete_one({'_id': oid})
    return redirect(url_for('blog.index'))



