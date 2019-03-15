from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for, abort
)

from artplace.auth import login_required

artpage = Blueprint('myart', __name__, url_prefix='/art')

@artpage.route('/')
@artpage.route('/myart')
@login_required
def art():
    return render_template('art/my_art.html')
