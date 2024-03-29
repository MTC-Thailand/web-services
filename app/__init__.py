import os

from flask import Flask
from flask_restful import Api
from dotenv import load_dotenv
from sqlalchemy.ext.automap import automap_base
from sqlalchemy import create_engine

from app.extensions import db, ma, migrate

load_dotenv()


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URI')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = os.environ.get('SQLALCHEMY_TRACK_MODIFICATIONS', False)
db.init_app(app)
ma.init_app(app)
migrate.init_app(app, db)

with app.app_context():
    Base = automap_base()
    mtc_engine = create_engine(os.environ.get('MTC_DATABASE_URI'))
    Base.prepare(mtc_engine, reflect=True)


from app.api import api as api_blueprint

api = Api(api_blueprint)

# add resources here
from app.api.views import MemberResource, MemberPIDResource, MemberMOPHResource

api.add_resource(MemberResource, '/mtc/member/<int:mem_id>')
api.add_resource(MemberPIDResource, '/mtc/member/pid/<int:pid>')
api.add_resource(MemberMOPHResource, '/moph/member/<int:mem_id>')


app.register_blueprint(api_blueprint)