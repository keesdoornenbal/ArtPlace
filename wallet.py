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
        'SELECT w.balance, id'
        ' FROM wallet w WHERE w.owner_id = ?',
        (id,)
    ).fetchone()
    contracts = db.execute(
        'SELECT c.id, enddate, price, artpiece_id, borrower_id, image, imagetype, value, artpiecename, username'
        ' FROM contract c JOIN artpiece a ON c.artpiece_id = a.id '
        ' JOIN user u ON c.borrower_id = u.id  '
        ' WHERE borrower_id IS NOT NULL AND lender_id = ?',
        (id,)
    ).fetchall()
    return render_template('wallet/wallet.html', wallet=wallet, contracts=contracts)

@bp.route('/deposit', methods=('GET', 'POST'))
@login_required
def deposit():
    amount = float(request.form['deposit_new'])
    amount = round(amount,2)
    wallet_id = request.form['wallet_id']
    db = get_db()
    wallet = db.execute(
        'SELECT w.balance, id'
        ' FROM wallet w WHERE w.id = ?',
        (wallet_id,)
    ).fetchone()
    new_balance = wallet['balance'] + amount
    db.execute(
        'UPDATE wallet SET balance = ?'
        ' WHERE id = ?',
        (new_balance, wallet_id)
    )
    db.commit()
    return redirect(url_for('wallet.index'))
