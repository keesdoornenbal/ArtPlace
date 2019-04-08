from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for, session
)
from werkzeug.exceptions import abort
from werkzeug.security import check_password_hash, generate_password_hash

from artplace.auth import login_required
from artplace.db import get_db

bp = Blueprint('index', __name__)

@bp.route('/')
@bp.route('/index')
def index():
    return render_template('homepage/index.html')


@bp.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        username = request.form['login_username']
        password = request.form['login_password']
        db = get_db()
        error = None
        user = db.execute(
            'SELECT * FROM user WHERE username = ?', (username,)
        ).fetchone()

        if user is None:
            error = 'Incorrect username.'
        elif not check_password_hash(user['password'], password):
            error = 'Incorrect password.'

        if error is None:
            session.clear()
            session['user_id'] = user['id']
            return redirect(url_for('explore.index'))

        flash(error)
    return render_template('homepage/index.html')


@bp.route('/register', methods=('GET', 'POST'))
def register():
    username = request.form['register_username']
    password = request.form['register_password']
    passwordcheck = request.form['register_password_check']
    db = get_db()
    error = None

    if not username:
        error = 'Username is required.'
    elif not password:
        error = 'Password is required.'
    elif password != passwordcheck:
        error = "Passwords don't match."
    elif db.execute(
        'SELECT id FROM user WHERE username = ?', (username,)
    ).fetchone() is not None:
        error = 'User {} is already registered.'.format(username)

    if error is None:
        db.execute(
            'INSERT INTO user (username, password) VALUES (?, ?)',
            (username, generate_password_hash(password))
        )
        db.commit()
        session.clear()
        user = db.execute(
            'SELECT * FROM user WHERE username = ?', (username,)
        ).fetchone()
        session['user_id'] = user['id']
        return redirect(url_for('explore.index'))
    else:
        flash(error)
        return render_template('homepage/index.html')
