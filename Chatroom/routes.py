""" Routes for page content """
from flask import Blueprint, render_template, request, flash, jsonify
from flask_login import current_user, login_required
from flask_socketio import emit
from .models import *
from .import socketio

# Blueprint Configuration
main_bp = Blueprint(
    'main_bp', __name__,
    template_folder='templates',
    static_folder='static'
)

@main_bp.route("/dashboard", methods=["GET", "POST"])
@login_required
def dashboard(): 
    return render_template("dashboard.html")

### CREATE NEW CHANNEL ###
@main_bp.route("/add_channel", methods=["POST"])
def add_channel():
    channel_name = request.form.get("channel_name")

    # Check if the channel already exists in database
    existing_channel = Channel.query.filter_by(name=channel_name).first()

    # Only add new channel
    if existing_channel is None:
        # Create new channel associated with current_user
        current_user.create_channel(channel_name)
        return jsonify({"success": True})
    else:
        return jsonify({"success": False})

### SEND A NEW MESSAGE IN A CHANNEL ###
@socketio.on("add message")
def add_message(data):
    # Retrieve info of message
    message = data["message"]
    channel_name = data["channel_name"]

    # Get channel id
    channel_id = Channel.query.filter_by(name=channel_name).first().id

    # Add message to database
    timestamp = current_user.send_message(message=message, channel_id=channel_id)

    # Broadcast the message to all users in that channel
    emit("announce message", {"message": message, "author": current_user.username, "timestamp": timestamp.strftime('%H:%M')}, broadcast=True)

### LOAD ALL CHANNELS ASSOCIATING WITH USER ###
@main_bp.route("/load_channels", methods=["GET"])
def load_channels():
    # Get a JSON serialized version of channels
    channels = [channel.name for channel in current_user.channels]

    return jsonify({"channels": channels})

### LOAD INFORMATION OF A CHANNEL ###
@main_bp.route("/load_channel_info", methods=["POST"])
def load_channel_info():
    channel_name = request.form.get("channel_name")

    # Get channel info
    channel = Channel.query.filter_by(name=channel_name).first()

    messages, members = [], []

    # Get a JSON serialized version of message history from database
    for message in channel.messages:
        # Initialize a JSON object
        msg = {
            "message": message.message,
            "author": message.author,
            "timestamp": message.timestamp.strftime('%H:%M')
        }

        # Append message to array
        messages.append(msg)

    # Get a JSON serialized version of members from database
    for member in channel.members:
        # Initialize a JSON object
        mem = {"username": member.username}

        # Append member to array
        members.append(mem)

    return jsonify({"channel_name": channel_name, "messages": messages, "members": members})

### INVITE ANOTHER USER TO CHANNEL ###
@main_bp.route("/send_invitation", methods=["POST"])
def send_invitation(): 
    username = request.form.get("username")
    channel = request.form.get("channel")

    # Check if the user already exists in database
    existing_user = User.query.filter_by(username=username).first()

    # Send invitation
    if existing_user:
        # Create new channel associated with current_user
        current_user.invite(invitee=username, channel=channel)
        return jsonify({"success": True})
    else:
        return jsonify({"success": False})

### CLEAR INVITATION USER HAS ALREADY SELECTED ###
@main_bp.route("/clear_invitation", methods=["POST"])
def clear_invitation():
    invitation_id = request.form.get("invitation_id")
    invitation = Invitation.query.get(invitation_id)
    db.session.delete(invitation)
    db.session.commit()
    return jsonify({"success": True})

### LOAD ALL PENDING INVITATIONS USER CURRENTLY HAS ###
@main_bp.route("/load_invitations", methods=["GET"])
def load_invitations():
    invitations = []

    # Get a JSON serialized version of pending invitations
    for invitation in current_user.invitations:
        invitations.append({"host": invitation.host, 
                            "channel": invitation.channel,
                            "id": invitation.id
                        })

    return jsonify({"invitations": invitations})

### JOIN A CHANNEL ###
@main_bp.route("/join_channel", methods=["POST"])
def join_channel():
    channel_name = request.form.get("channel_name")

    # Get channel object
    channel = Channel.query.filter_by(name=channel_name).first()

    current_user.join(channel)
    if channel:
        return jsonify({"success": True})
    else:
        return jsonify({"success": False})

