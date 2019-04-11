import os
import random, string
import base64
from datetime import datetime

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
    id = g.user['id']
    artpieces = db.execute(
        'SELECT a.id, artpiecename, image, uploadtime, owner_id, username, renter_id, imagetype, value'
        ' FROM artpiece a JOIN user u ON a.owner_id = u.id'
        ' WHERE a.owner_id = ? OR renter_id = ?'
        ' ORDER BY uploadtime DESC',
        (id, id,)
    ).fetchall()

    return render_template('art/my_art.html', artpieces=artpieces)

@artpage.route('/upload', methods=('GET', 'POST'))
@login_required
def upload():
    title = request.form['title_new']
    value = float(request.form['value_new'])
    value = round(value,2)
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
            'INSERT INTO artpiece (artpiecename, image, owner_id, imagetype, value)'
            ' VALUES (?, ?, ?, ?, ?)',
            (title, data, g.user['id'], file_extension, value)
        )
        db.commit()
        return redirect(url_for('myart.art'))

@artpage.route('/<int:id>/edit', methods=('GET', 'POST'))
@login_required
def edit(id):
    title = request.form['title_edit']
    value = float(request.form['value_edit'])
    value = round(value,2)
    error = None
    db = get_db()
    if 'image_edit' not in request.files:
        if not title:
            error = 'Title is required.'

        if error is not None:
            flash(error)
        else:
            db.execute(
                'UPDATE artpiece SET artpiecename = ?, owner_id = ?, value = ?'
                ' WHERE id = ?',
                (title, g.user['id'], value, id)
            )
            db.commit()
            return redirect(url_for('myart.art'))
    else:
        file = request.files['image_edit']
        filename, file_extension = os.path.splitext(file.filename)
        file_extension = file_extension.replace('.', '')

        if not title:
            error = 'Title is required.'

        if error is not None:
            flash(error)
        else:
            data = str(base64.b64encode(file.read()))
            data = data.replace("b'", '')
            data = data.replace("'", '')
            db.execute(
                'UPDATE artpiece SET artpiecename = ?, image = ?, owner_id = ?, imagetype = ?, value = ?'
                ' WHERE id = ?',
                (title, data, g.user['id'], file_extension, value, id)
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
    date = request.form['enddate_new']
    date = datetime.strptime(date, '%d-%m-%Y')
    price = float(request.form['price_new'])
    price = round(price,2)
    error = None

    if not title:
        error = 'Title is required.'

        if not title:
            error = 'Something wrong with the artpiece.'

    if error is not None:
        flash(error)
    else:
        userid = g.user['id']
        db = get_db()
        db.execute(
            'INSERT INTO contract (artpiece_id, enddate, price, lender_id)'
            ' VALUES (?, ?, ?, ?)',
            (artpiece, date, price, userid)
        )
        db.commit()
        contract = db.execute(
            'SELECT c.id, artpiece_id, lender_id'
            ' FROM contract c'
            ' WHERE c.artpiece_id = ? AND c.lender_id = ?',
            (artpiece, userid)
        ).fetchone()
        db.execute(
            'INSERT INTO post (title, body, author_id, contract_id)'
            ' VALUES (?, ?, ?, ?)',
            (title, body, g.user['id'], contract['id'])
        )
        db.commit()
        return redirect(url_for('myart.art'))
