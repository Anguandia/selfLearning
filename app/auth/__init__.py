from flask import Blueprint
# import app.models

bp = Blueprint('auth', __name__, url_prefix='/api/v1/auth')

from . import views
