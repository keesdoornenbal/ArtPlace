from datetime import datetime

from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)

from artplace.auth import login_required
from artplace.db import get_db

bp = Blueprint('explore', __name__, url_prefix='/explore')

def get_post(id, check_author=True):
    post = get_db().execute(
        'SELECT p.id, title, body, created, author_id, username'
        ' FROM post p JOIN user u ON p.author_id = u.id'
        ' WHERE p.id = ?',
        (id,)
    ).fetchone()

    if post is None:
        abort(404, "Post id {0} doesn't exist.".format(id))

    if check_author and post['author_id'] != g.user['id']:
        abort(403)

    return post

@bp.route('/')
@bp.route('/index')
@login_required
def index():
    db = get_db()
    posts = db.execute(
        'SELECT p.id, title, body, created, author_id, username, contract_id, enddate, price, lender_id, artpiece_id, image, imagetype, artpiecename, value'
        ' FROM post p JOIN user u ON p.author_id = u.id'
        ' LEFT JOIN contract c ON p.contract_id = c.id'
        ' LEFT JOIN artpiece a ON c.artpiece_id = a.id'
        ' ORDER BY created DESC'
    ).fetchall()
    wallet = db.execute(
        'SELECT w.id, owner_id, balance'
        ' FROM wallet w'
        ' WHERE owner_id = ?',
        (g.user['id'],)
    ).fetchone()

    return render_template('explore/explore.html', posts=posts, wallet=wallet)

@bp.route('/create', methods=('GET', 'POST'))
@login_required
def create():
    title = request.form['title_new']
    body = request.form['body_new']
    error = None

    if not title:
        error = 'Title is required.'

    if error is not None:
        flash(error)
    else:
        db = get_db()
        db.execute(
            'INSERT INTO post (title, body, author_id)'
            ' VALUES (?, ?, ?)',
            (title, body, g.user['id'])
        )
        db.commit()
        return redirect(url_for('explore.index'))


@bp.route('/edit', methods=('GET', 'POST'))
@login_required
def edit():
    id = request.form['post_id']
    post = get_post(id)
    title = request.form['title_edit']
    body = request.form['body_edit']
    error = None

    if not title:
        error = 'Title is required.'

    if error is not None:
        flash(error)
    else:
        db = get_db()
        db.execute(
            'UPDATE post SET title = ?, body = ?'
            ' WHERE id = ?',
            (title, body, id)
        )
        db.commit()
        return redirect(url_for('explore.index'))

@bp.route('/<int:id>/delete', methods=('GET', 'POST'))
@login_required
def delete(id):
    get_post(id)
    db = get_db()
    db.execute('DELETE FROM post WHERE id = ?', (id,))
    db.commit()
    return redirect(url_for('explore.index'))


@bp.route('/rent', methods=('GET', 'POST'))
@login_required
def rent():
    db = get_db()
    contract_id = request.form['contract_id']
    wallet_id = request.form['wallet_id']
    price = float(request.form['price'])
    post_id = request.form['post_id']
    artpiece_id = request.form['artpiece_id']
    owner_id = request.form['owner']
    # heerlijk gemaakt dit
    db.execute(
        'UPDATE contract SET borrower_id = ?'
        ' WHERE id = ?',
        (g.user['id'], contract_id)
    )
    wallet = db.execute(
        'SELECT w.id, balance'
        ' FROM wallet w'
        ' WHERE id = ?',
        (wallet_id,)
    ).fetchone()
    new_balance = wallet['balance'] - price
    db.execute(
        'UPDATE wallet SET balance = ?'
        ' WHERE id = ?',
        (new_balance, wallet_id)
    )
    db.execute(
        'UPDATE artpiece SET renter_id = ?'
        ' WHERE id = ?',
        (g.user['id'], artpiece_id)
    )
    db.execute('DELETE FROM post WHERE id = ?', (post_id,))
    owner_wallet = db.execute(
        'SELECT w.id, balance, owner_id'
        ' FROM wallet w'
        ' WHERE owner_id = ?',
        (owner_id,)
    ).fetchone()
    owner_balance = owner_wallet['balance'] + price
    db.execute(
        'UPDATE wallet SET balance = ?'
        ' WHERE id = ?',
        (owner_balance, owner_wallet['id'])
    )
    db.commit()
    return redirect(url_for('explore.index'))
