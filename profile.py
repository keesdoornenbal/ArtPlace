from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)

from artplace.auth import login_required
from artplace.db import get_db

bp = Blueprint('profile', __name__, url_prefix='/explore')
