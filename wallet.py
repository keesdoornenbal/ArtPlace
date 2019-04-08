from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)

from artplace.auth import login_required
from artplace.db import get_db

bp = Blueprint('wallet', __name__, url_prefix='/wallet')

@bp.route('/')
@bp.route('/index')
@login_required
def index():
    db = get_db()
    id = g.user['id']
    wallet = db.execute(
        'SELECT w.balance'
        ' FROM wallet w WHERE w.owner_id = ?',
        (id,)
    ).fetchone()
    return render_template('wallet/wallet.html', wallet=wallet)
