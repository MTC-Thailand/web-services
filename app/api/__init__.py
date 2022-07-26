from flask import Blueprint

api = Blueprint('api', __name__, url_prefix='/apis/v1')


from . import views