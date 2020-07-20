""" Database models. """
from .import db
from datetime import datetime, timezone
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
    messages = db.relationship("Message", backref="user", lazy=True)

    # Each user will have a record of invitations to join other channels
    invitations = db.relationship("Invitation", backref="user", lazy=True)

    def send_message(self, message, channel_id):
        new_message = Message(message=message, author=self.username, channel_id=channel_id)
        db.session.add(new_message)
        db.session.commit()

        # Return id & time of message
        return [new_message.id, new_message.timestamp]

    def create_channel(self, channel_name):
        new_channel = Channel(name=channel_name)

        # Creator of new channel will be the first to be appended to channel
        new_channel.members.append(self)

        # Add channel to database
        db.session.add(new_channel)
        db.session.commit()

    def invite(self, invitee, channel):
        new_invitation = Invitation(host=self.username, invitee=invitee, channel=channel)

        # Add invitation to database
        db.session.add(new_invitation)
        db.session.commit()

    def join(self, channel):
        # Add user to the channel
        channel.members.append(self)
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

    # Message
    message = db.Column(db.String, nullable=False)

    # Name of author
    author = db.Column(db.String, db.ForeignKey('users.username'), nullable=False)

    # Channel ID
    channel_id = db.Column(db.Integer, db.ForeignKey('channels.id'), nullable=False)

    # Time when the message was made
    # No need to worry about this since we already default it to "now"
    timestamp = db.Column(db.DateTime(), default=datetime.now, index=True)

class Invitation(db.Model):
    __tablename__ = "invitations"
    # an easy way to reference each invitation
    id = db.Column(db.Integer, primary_key=True)

    # Host (User who invite)
    host = db.Column(db.String, nullable=False)

    # Invitee (User who receive invitation)
    invitee = db.Column(db.String, db.ForeignKey('users.username'), nullable=False)

    # Channel (Which channel to join)
    channel = db.Column(db.String, nullable=False)