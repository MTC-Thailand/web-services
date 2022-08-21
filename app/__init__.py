import os

from flask import Flask
from flask_restful import Api
from dotenv import load_dotenv
from sqlalchemy.ext.automap import automap_base

from app.extensions import db, ma

load_dotenv()


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URI')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = os.environ.get('SQLALCHEMY_TRACK_MODIFICATIONS', False)
db.init_app(app)
ma.init_app(app)

with app.app_context():
    Base = automap_base()
    Base.prepare(db.engine, reflect=True)


from app.api import api as api_blueprint

api = Api(api_blueprint)

# add resources here
from app.api.views import MemberResource, MemberPIDResource, MemberINETResource

api.add_resource(MemberResource, '/member/<int:mem_id>')
api.add_resource(MemberPIDResource, '/member/pid/<int:pid>')
api.add_resource(MemberINETResource, '/inet/member/<int:mem_id>')


app.register_blueprint(api_blueprint)