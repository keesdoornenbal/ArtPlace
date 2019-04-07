import os
import random, string
import base64

from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for, abort
)

from flask import current_app as app

from artplace.auth import login_required
from artplace.db import get_db

artpage = Blueprint('myart', __name__, url_prefix='/art')

def get_artpiece(id, check_author=True):
    artpiece = get_db().execute(
        'SELECT a.id, artpiecename, image, uploadtime, owner_id, imagetype'
        ' FROM artpiece a JOIN user u ON a.owner_id = u.id'
        ' WHERE a.id = ?',
        (id,)
    ).fetchone()

    if artpiece is None:
        abort(404, "Artpiece id {0} doesn't exist.".format(id))

    if check_author and artpiece['owner_id'] != g.user['id']:
        abort(403)

    return artpiece

@artpage.route('/')
@artpage.route('/myart')
@login_required
def art():
    db = get_db()
    artpieces = db.execute(
        'SELECT a.id, artpiecename, image, uploadtime, owner_id, imagetype'
        ' FROM artpiece a JOIN user u ON a.owner_id = u.id'
        ' ORDER BY uploadtime DESC'
    ).fetchall()

    return render_template('art/my_art.html', artpieces=artpieces)

@artpage.route('/upload', methods=('GET', 'POST'))
@login_required
def upload():
    title = request.form['title_new']
    if 'image_new' not in request.files:
        flash('No file uploaded!')
        return redirect(url_for('myart.art'))
    file = request.files['image_new']
    filename, file_extension = os.path.splitext(file.filename)
    file_extension = file_extension.replace('.', '')
    error = None

    if not title:
        error = 'Title is required.'

    if error is not None:
        flash(error)
    else:
        db = get_db()
        data = str(base64.b64encode(file.read()))
        data = data.replace("b'", '')
        data = data.replace("'", '')
        db.execute(
            'INSERT INTO artpiece (artpiecename, image, owner_id, imagetype)'
            ' VALUES (?, ?, ?, ?)',
            (title, data, g.user['id'], file_extension)
        )
        db.commit()
        return redirect(url_for('myart.art'))

@artpage.route('/<int:id>/delete', methods=('GET', 'POST'))
@login_required
def delete(id):
    get_artpiece(id)
    db = get_db()
    posts = db.execute(
        'SELECT p.id'
        ' FROM post p JOIN artpiece a ON p.artpiece_id = a.id'
        ' ORDER BY created DESC'
    ).fetchall()
    db.execute('DELETE FROM artpiece WHERE id = ?', (id,))
    db.execute('DELETE FROM post WHERE artpiece_id = ?', (id,))
    db.commit()
    return redirect(url_for('myart.art'))



@artpage.route('/<int:id>/post', methods=('GET', 'POST'))
@login_required
def post(id):
    artpiece = request.form['artpiece_id']
    title = request.form['title_new']
    body = request.form['body_new']
    error = None

    if not title:
        error = 'Title is required.'

        if not title:
            error = 'Something wrong with the artpiece.'

    if error is not None:
        flash(error)
    else:
        db = get_db()
        db.execute(
            'INSERT INTO post (title, body, author_id, artpiece_id)'
            ' VALUES (?, ?, ?, ?)',
            (title, body, g.user['id'], artpiece)
        )
        db.commit()
        return redirect(url_for('myart.art'))
