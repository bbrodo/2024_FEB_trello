from datetime import date

from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity

from init import db
from models.comment import Comment, comment_schema, comments_schema
from models.card import Card
from json import dump

comments_bp = Blueprint("comments", __name__, url_prefix="/<int:card_id>/comments")

@comments_bp.route("/", methods=["POST"])

@jwt_required()

def create_comment(card_id):

    # get the comment object from the request body

    body_data = request.get_json()

    # fetch the card with that particular id - card_id

    stmt = db.select(Card).filter_by(id=card_id)

    card = db.session.scalar(stmt)

    # if card exists

    if card:

        # create an instance of the Comment model

        comment = Comment(

            message=body_data.get("message"),

            date=date.today(),

            card=card,

            user_id=get_jwt_identity()

        )

        # add and commit the session

        db.session.add(comment)

        db.session.commit()

        # return the created commit

        return comment_schema.dump(comment), 201

    # else

    else:

        # return an error like card does not exist

        return {"error": f"Card with id {card_id} not found"}, 404

@comments_bp.route("/<int:comment_id>", methods=["DELETE"])
@jwt_required()
def delete_comment(card_id, comment_id):
    stmt = db.select(Comment).filter_by(id=comment_id)
    comment = db.session.scalar(stmt)

    if comment:
        db.session.delete(comment)
        db.session.commit()

        return {"message": f"comment '{comment.message}' deleted successfully"}
    else:
        return {"error": f"comment with id {comment_id} does not exist"}, 404
    

@comments_bp.route("/<int:comment_id>", methods=["PATCH", "PUT"])
@jwt_required()
def edit_comment(card_id, comment_id):
    body_data = request.get_json()
    stmt = db.select(Comment).filter_by(id=comment_id)
    comment = db.session.scalar(stmt)

    if comment:
        comment.message = body_data.get("message") or comment.message
        db.session.commit()
        return comment_schema.dump(comment)
    else:
        return {"error": f"comment with id {comment_id} not found"}, 404
