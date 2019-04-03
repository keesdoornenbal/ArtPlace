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

@artpage.route('/')
@artpage.route('/myart')
@login_required
def art():
    db = get_db()
    artpieces = db.execute(
        'SELECT a.title, image, created, owner_id, imagetype'
        ' FROM artpiece a JOIN user u WHERE a.owner_id = u.id'
        ' ORDER BY created DESC'
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
            'INSERT INTO artpiece (title, image, owner_id, imagetype)'
            ' VALUES (?, ?, ?, ?)',
            (title, data, g.user['id'], file_extension)
        )
        db.commit()
        return redirect(url_for('myart.art'))
