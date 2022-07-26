from marshmallow_sqlalchemy import SQLAlchemyAutoSchema, auto_field


from app import Base


Member = Base.classes.member


class MemberSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Member
        load_instance = True