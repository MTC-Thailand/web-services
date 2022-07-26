from flask_restful import Resource

from app.extensions import db
from app.api.schema import Member, MemberSchema


class MemberResource(Resource):
    def get(self, mem_id):
        member = db.session.query(Member).get_or_404(mem_id)
        member_schema = MemberSchema()
        print(member.fname, member.lname, member.mem_id)
        return {'data': member_schema.dumps(member)}