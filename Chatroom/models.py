""" Database models. """
from .import db
from datetime import datetime
from flask_login import UserMixin

# Create an association table for many-to-many relationship between users and channels
mems = db.Table('mems', 
    db.Column('user_id', db.Integer, db.ForeignKey('users.id'), primary_key=True), 
    db.Column('channel_id', db.Integer, db.ForeignKey('channels.id'), primary_key=True)
)

class User(UserMixin, db.Model):
    __tablename__ = "users"
    # an easy way to reference each user
    id = db.Column(db.Integer, primary_key=True)

    # Duplicate emails/usernames are not allowed
    # nullable = False -> can't be blank
    email = db.Column(db.String, unique=True, nullable=False)
    username = db.Column(db.String, unique=True, nullable=False)
    password = db.Column(db.String, nullable=False)

    # Declare a relationship between User and Channel
    # A secondary relationship is required because we're implementing many-to-many relationship
    channels = db.relationship("Channel", secondary=mems, backref=db.backref('members', lazy= 'dynamic'))

    # Declare a relationship between User and Message
    messages = db.relationship("Message", backref="user",lazy=True)

    def write_message(self, text, channel_id):
        message = Message(text=text, author=self.username, channel_id=channel_id)
        db.session.add(message)
        db.session.commit()

    def create_channel(self, channel_name):
        new_channel = Channel(name=channel_name)

        # Creator of new channel will be the first to be appended to channel
        new_channel.members.append(self)

        # Add channel to database
        db.session.add(new_channel)
        db.session.commit()

class Channel(db.Model):
    __tablename__ = "channels"
    # an easy way to reference each channel
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, unique=True, nullable=False)

    messages = db.relationship("Message", backref="channel", lazy=True)

class Message(db.Model):
    __tablename__ = "messages"
    # an easy way to reference each message
    id = db.Column(db.Integer, primary_key=True)

    # Typed message from users
    text = db.Column(db.String, nullable=False)

    # Name of author
    author = db.Column(db.String, db.ForeignKey('users.username') , nullable=False)

    # Channel ID
    channel_id = db.Column(db.Integer, db.ForeignKey('channels.id'), nullable=False)

    # Time when the message was made
    # No need to worry about this since we already default it to "now"
    timestamp = db.Column(db.DateTime(), default=datetime.utcnow, index=True)