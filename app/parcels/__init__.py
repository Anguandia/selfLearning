from flask import Blueprint

parcels_bp = Blueprint('parcels', __name__, url_prefix='/api/v1')

from . import views
import app.models
