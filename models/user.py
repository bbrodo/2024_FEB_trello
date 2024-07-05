from init import db, ma
from marshmallow import fields
from marshmallow.validate import Regexp

class User(db.Model):
    # name of table
    __tablename__ = "users"

    # attributes
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    email = db.Column(db.String, nullable=False, unique=True)
    password = db.Column(db.String, nullable=False)
    is_admin = db.Column(db.Boolean, default=False)

    cards = db.relationship('Card', back_populates='user')
    comments = db.relationship("Comment", back_populates="user")


class UserSchema(ma.Schema):

    cards = fields.List(fields.Nested('CardSchema', exclude=["user"]))
    comments = fields.List(fields.Nested('CommentSchema', exclude=["user"]))

    email = fields.String(required=True, validate=Regexp("^\S+@\S+\.\S+$", error="Invalid email format"))

    password = fields.String(required=True, validate=Regexp("^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d]{8,}$", error="Password must contain a minimum of eight characters, at least one letter and one number"))

    class Meta:
        fields = ("id", "name", "email", "password", "is_admin", "cards", "comments")

# to handle one user
user_schema = UserSchema(exclude=["password"])

# to handle many users
users_schema = UserSchema(many=True, exclude=["password"])