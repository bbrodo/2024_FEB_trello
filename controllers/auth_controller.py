from flask import Blueprint, request
from sqlalchemy.exc import IntegrityError
from psycopg2 import errorcodes
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from init import bcrypt, db
from datetime import timedelta
from models.user import User, user_schema, UserSchema

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")

@auth_bp.route("/register", methods=["POST"])
def register_user():
    try:
        # get the body data
        body_data = UserSchema().load(request.get_json())
        # create user model
        user = User(
            name=body_data.get("name"),
            email=body_data.get("email")
        )
        # hash password
        password = body_data.get("password")

        if password:
            user.password = bcrypt.generate_password_hash(password).decode("utf-8")

        # commit 
        db.session.add(user)
        db.session.commit()
        # respond
        return user_schema.dump(user), 201
    # error check
    except IntegrityError as err:
        if err.orig.pgcode == errorcodes.NOT_NULL_VIOLATION:
            # not null violation
            return {"error": f"The column {err.orig.diag.column_name} is required"}, 409
        if err.orig.pgcode == errorcodes.UNIQUE_VIOLATION:
            # unique violation
            return {"error": "Email address is already in use"}, 409


@auth_bp.route("/login", methods=["POST"])
def login_user():
    # get the data
    body_data = request.get_json()
    # find user in db
    stmt = db.select(User).filter_by(email=body_data.get("email"))
    user = db.session.scalar(stmt)
    # if user exists and password is correct
    if user and bcrypt.check_password_hash(user.password, body_data.get("password")):
        # create jwt
        token = create_access_token(identity=str(user.id), expires_delta=timedelta(days=1))
        # respond
        return {"email": user.email, "is_admin": user.is_admin, "token": token}
    # else
    else:
        # respond with error
        return {"error": "Invalid email or password"}, 401
    
@auth_bp.route("/users/<int:user_id>", methods=["PUT", "PATCH"])
@jwt_required()
def update_user(user_id):
    body_data = UserSchema().load(request.get_json(), partial=True)
    password = body_data.get("password")
    stmt = db.select(User).filter_by(id=get_jwt_identity())
    user = db.session.scalar(stmt)

    if user:
        user.name = body_data.get("name") or user.name
        if password:
            user.password = bcrypt.generate_password_hash(password).decode("utf-8")
        db.session.commit()

        return user_schema.dump(user)
    else:
        return {"error": f"user with id '{user_id}' does not exist"}
    