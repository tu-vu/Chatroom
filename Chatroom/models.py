""" Database models. """
from .import db
from datetime import datetime
from flask_login import UserMixin

class User(UserMixin, db.Model):
    __tablename__ = "users"
    # an easy way to reference each user
    id = db.Column(db.Integer, primary_key=True)

    # Duplicate emails/usernames are not allowed
    # nullable = False -> can't be blank
    email = db.Column(db.String, unique=True, nullable=False)
    username = db.Column(db.String, unique=True, nullable=False)
    password = db.Column(db.String, nullable=False)
    image = db.Column(db.String, nullable = False)

    # Declare a relationship between User and Message
    # backref = users allows Message to refer back to user, e.g my_message.user
    # lazy = True means we will only load data when it's accessed
    messages = db.relationship("Message", backref="user",lazy=True)

    def write_message(self, text):
        message = Message(text=text, author=self.username)
        db.session.add(message)
        db.session.commit()

    def __repr__(self):
        return "<User {}>".format(self.username)

""" NEED TO ADD MORE CLASSES(e.g. CHANNEL) """

class Message(db.Model):
    __tablename__ = "messages"
    # an easy way to reference each message
    id = db.Column(db.Integer, primary_key=True)

    # Typed message from users
    text = db.Column(db.String, nullable=False)

    # Name of author
    author = db.Column(db.String, db.ForeignKey('users.username') , nullable=False)

    # Time when the message was made
    # No need to worry about this since we already default it to "now"
    timestamp = db.Column(db.DateTime(), default=datetime.utcnow, index=True)