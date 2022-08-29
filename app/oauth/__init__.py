from flask import Blueprint

oauth_bp = Blueprint('oath', __name__)

from . import views