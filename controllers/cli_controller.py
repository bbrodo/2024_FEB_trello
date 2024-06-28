from flask import Blueprint
from init import db, bcrypt
from models.user import User
from models.card import Card
from datetime import date
from models.comment import Comment

db_commands = Blueprint("db", __name__)

@db_commands.cli.command("create")
def create_tables():
    db.create_all()
    print("Tables created")

@db_commands.cli.command("drop")
def drop_tables():
    db.drop_all()
    print("Tables dropped")

@db_commands.cli.command("seed")
def seed_tables():
    # create a list of user instances
    users = [
        User(
            email="admin@gmail.com",
            password=bcrypt.generate_password_hash("123").decode("utf-8"),
            is_admin=True
        ),
        User(
            name="User 1",
            email="user1@gmail.com",
            password=bcrypt.generate_password_hash("123").decode("utf-8")
        )
    ]

    db.session.add_all(users)

    cards = [
        Card(
            title="Card 1",
            description="card 1 desc",
            date=date.today(),
            status="To do",
            priority="high",
            user=users[0]
        ),
        Card(
            title="card 2",
            description="card 2 desc",
            date=date.today(),
            status="ongoing",
            priority="low",
            user=users[0]
        ),
        Card(
            title="card 3",
            description="card 3 desc",
            date=date.today(),
            status="done",
            priority="medium",
            user=users[1]
        )
    ]

    db.session.add_all(cards)

    db.session.commit()

    print("Tables seeded")