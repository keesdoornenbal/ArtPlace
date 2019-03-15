from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)

from artplace.auth import login_required

bp = Blueprint('art', __name__, url_prefix='/art')

@bp.route('/')
@bp.route('/myart')
@login_required
def art():
    return render_template('art/my_art.html')
