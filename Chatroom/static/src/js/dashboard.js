document.addEventListener("DOMContentLoaded", function() {
    // CONNECT TO WEBSOCKET TO ALLOW FOR REALTIME COMMUNICATION
    var socket = io.connect(location.protocol + '//' + document.domain + ':' + location.port);

    // LOAD ALL CHANNELS ASSOCIATING WITH USER
    load_channels();

    // SET UP DEFAULT CONTENT FOR DASHBOARD
    load_dashboard();

    // HIDE MESSAGE HISTORY AND MESSAGE FORM BY DEFAULT
    document.querySelector("#messenger").style.display = "none";    

    // HIDE MEMBER LIST AND INVITE FORM BY DEFAULT
    document.querySelector("#membership").style.display = "none";

    // DISABLE SUBMIT BUTTONS BY DEFAULT
    document.querySelectorAll("input[type='submit']").forEach(function(button) {
        button.disabled = true;
    });

    // ONLY ENABLE SUBMIT BUTTONS WHEN USER TYPE SOMETHING
    document.querySelectorAll("input[type='text']").forEach(function(input_bar) {
        input_bar.onkeyup = function() {
            // Retrieve submit button
            const button = document.querySelector(`#${input_bar.id} ~ input`);

            // If input bar is not empty, enable button
            if (input_bar.value.length > 0) {
                button.disabled = false;
            } else {
                button.disabled = true;
            }
        };
    }); 

    // CREATE NEW CHANNEL
    document.querySelector("#new_channel").onsubmit = function() {
        // Retrieve channel name typed by user 
        const channel_name = document.querySelector("#channel_name").value;

        // Clear input bar
        document.querySelector("#channel_name").value = "";
        document.querySelector("#create").disabled = true;

        // Add new channel
        add_channel(channel_name);

        // Stop page from reloading
        return false;
    };

    // CONFIGURE BUTTON WHEN SOCKET CONNECTED
    socket.on("connect", function() {
        // SEND A NEW MESSAGE
        document.querySelector("#new_message").onsubmit = function() {
            // Retrieve message typed by user 
            const message = document.querySelector("#message").value;

            // Retrieve selected channel
            const active_channel = document.querySelector(".active");

            // Clear input bar
            document.querySelector("#message").value = "";
            document.querySelector("#send").disabled = true;

            // Emit(Start) event "send message" when message form is submitted
            socket.emit("add message", {"message": message, "channel_name": active_channel.innerHTML});

            // Stop page from reloading
            return false;
        };

        // USER CLICKED ONE OF CHANNEL
        document.querySelector("#channels").onclick = function(div_area) {
            // div_area.target is the clicked element!

            // Only apply changes if user click another button
            if (div_area.target && div_area.target.nodeName === "BUTTON") {
                const active_channel = div_area.target;

                // Hide dashboard
                document.querySelector("#dashboard").style.display = "none";

                // Show message history and form
                document.querySelector("#messenger").style.display = "";            

                // Show members list and form
                document.querySelector("#membership").style.display = "";

                // Get previously clicked channel
                const prev_channel = document.querySelector(".active");

                // No button is clicked yet
                if (prev_channel !== null) {
                    // Remove clicked status
                    prev_channel.className = prev_channel.className.replace(" active", "");

                    // Emit(Start) event "leave" previous channel when user click new channel
                    socket.emit("leave", {"channel_name": prev_channel.innerHTML});
                }

                // Set the clicked button to active until another button is clicked
                active_channel.className += " active";

                // Load all info of channel(message history, members, etc)
                load_channel_info(active_channel);

                // Emit(Start) event "join" when user enters the channel
                socket.emit("join", {"channel_name": active_channel.innerHTML});
            }
        };
    });

    // WHEN A NEW MESSAGE IS SENT, DISPLAY IT TO EVERYONE IN CHANNEL
    socket.on("announce message", function(data) {
        // Create new message tag
        const p = document.createElement('p');

        // Set content of message tag
        p.innerHTML = data.author + ": " + data.message + " [" + data.timestamp + "]";

        // Append new message to messages
        document.querySelector("#messages").append(p);

        // Adding delete button for each message
        const button = document.createElement('button');

        //set content of the button
        button.innerHTML = "[x]";

        // Append the button to the div
        document.querySelector("#messages").append(button);
    });

    // REMOVE A MESSAGE (UPDATE THIS IN DATABASE)
    document.querySelector("#messages").onclick = function(div_area) {
        const targetId = div_area.target;
        if(targetId.tagName !== "BUTTON") 
            return;

        targetId.previousSibling.remove();
        targetId.remove();
    };

    // INVITE ANOTHER USER TO JOIN SELECTED CHANNEL
    document.querySelector("#new_member").onsubmit = function() {
        // Retrieve usename typed by user 
        const username = document.querySelector("#username").value;        

        // Get active channel
        const active_channel = document.querySelector(".active");   

        // Clear input bar
        document.querySelector("#username").value = "";
        document.querySelector("#invite").disabled = true;

        // Send invitation
        send_invitation(username, active_channel.innerHTML);

        // Stop page from reloading
        return false;
    }

    // USER CLICK ACCEPT/DECLINE AN INVITATION
    document.querySelector("#dashboard").onclick = function(div_area) {
        // div_area.target is the clicked element!

        // Only apply changes if user click a button
        if (div_area.target && div_area.target.nodeName === "INPUT") {
            invitation = div_area.target.parentElement;

            // Get channel name
            channel_name = invitation.dataset.channel_name;

            // Check if user accept or decline invitation
            if (div_area.target.id === "accept") {
                join_channel(channel_name);

                // Add channel to field
                document.querySelector("#channels").innerHTML += `<button class='channel'>${channel_name}</button>`;
            } 

            // Clear invitation in database
            clear_invitation(invitation.id);
            invitation.remove();

            // Check if there is any invitation left 
            if(document.querySelector("#dashboard form") === null) {
                document.querySelector("#dashboard").innerHTML += "<p>Yout have no pending invitation</p>";
            }
        }
        return false;
    };
});

// LOAD EXISTING CHANNELS FOR USER
function load_channels() {
    // Initialize a new request
    const request = new XMLHttpRequest();
    request.open('GET', '/load_channels');

    request.onload = function() {
        // Extract JSON data from object
        const data = JSON.parse(request.responseText);

        // Traverse and print all channels
        for (channel_name of data.channels) {
            // Add channel to field
            document.querySelector("#channels").innerHTML += `<button class='channel'>${channel_name}</button>`;
        }
    };

    // Send request
    request.send();
}

// LOAD MESSAGE HISTORY OF THE CHANNEL
function load_channel_info(channel) {
    // Initialize a new request
    const request = new XMLHttpRequest();
    request.open("POST", "/load_channel_info")

    // Callback function when request completes
    request.onload = function() {
        const data = JSON.parse(request.responseText);
        const messages = document.querySelector("#messages");        
        const members = document.querySelector("#members");

        // Reset message history
        messages.innerHTML = `<h3>Here is messages history for ${channel.innerHTML} </h3>`;

        // Reset members
        members.innerHTML = "";

        // Display message history
        for(message of data.messages) {
            messages.innerHTML += `<p>${message.author}: ${message.message} [${message.timestamp}]</p><button>[x]</button>`;
        }

        // Display members of channel
        for(member of data.members) {
            members.innerHTML += `<li>${member.username}</li>`;
        }
    };

    // Add data to send with request
    const data = new FormData();
    data.append("channel_name", channel.innerHTML);

    // Send request 
    request.send(data);
}

// LOAD CONTENT OF DASHBOARD
function load_dashboard() {
    const dashboard = document.querySelector("#dashboard");

    // Append header
    dashboard.innerHTML += "<h3>Here is the dashboard, when no channel is selected</h3>";

    // Initialize a new request
    const request = new XMLHttpRequest();
    request.open('GET', '/load_invitations');

    request.onload = function() {
        // Extract JSON data from object
        const data = JSON.parse(request.responseText);

        // Check if there's any invitation from other users
        if (!data.invitations || !data.invitations.length) {
            dashboard.innerHTML += "<p>Yout have no pending invitation</p>";
            return;
        }

        // Traverse and print all invitations
        for (invitation of data.invitations) {
            // Create invitation form 
            const form = document.createElement('form');
            form.id = "i" + invitation.id;
            form.dataset.channel_name = invitation.channel;
            form.style.backgroundColor = "#5dadec";

            const notification = `User ${invitation.host} invited you to join channel ${invitation.channel}`;

            const accept = "<input type='submit' id='accept' value='Accept'></input>";

            const decline = "<input type='submit' id='decline' value='Decline'></input>";

            form.innerHTML += notification + accept + decline

            // Add button to field
            dashboard.append(form);
        }
    };

    // Send request
    request.send();
}

// ADD NEW CHANNEL 
function add_channel(channel_name) {
    // Initialize a new request
    const request = new XMLHttpRequest();
    request.open('POST', '/add_channel');

    // When the request is loaded successfully
    request.onload = function() {
        // Extract JSON data from request
        const data = JSON.parse(request.responseText);

        // If creation of new channel is successful
        if(data.success) {
            // Add channel to field
            document.querySelector("#channels").innerHTML += `<button class='channel'>${channel_name}</button>`;
        } else {
            alert(`Sorry, channel ${channel_name} already exists`);
        }
    };

    // Add data to send with request
    const data = new FormData();
    data.append("channel_name", channel_name);

    // Send request
    request.send(data);
}

// SEND INVITATION TO ANOTHER USER
function send_invitation(username, channel_name) {
    // Initialize a new request
    const request = new XMLHttpRequest();
    request.open('POST', '/send_invitation');

    // When the request is loaded successfully
    request.onload = function() {
        // Extract JSON data from request
        const data = JSON.parse(request.responseText);

        // If creation of new channel is successful
        if(data.success) {
            alert(`Success!, user ${username} has received your invitation`);
        } else {
            alert(`Sorry, user ${username} does not exist`);
        }
    };

    // Add data to send with request
    const data = new FormData();
    data.append("username", username);
    data.append("channel_name", channel_name);

    // Send request
    request.send(data);
}

// JOIN A CHANNEL 
function join_channel(channel_name) {
    // Initialize a new request
    const request = new XMLHttpRequest();
    request.open('POST', '/join_channel');

    // When the request is loaded successfully
    request.onload = function() {
        // Extract JSON data from request
        const data = JSON.parse(request.responseText);
    };

    // Add data to send with request
    const data = new FormData();
    data.append("channel_name", channel_name);

    // Send request
    request.send(data);
}

// CLEAR INVITATION
function clear_invitation(invitation) {
    // Initialize a new request
    const request = new XMLHttpRequest();
    request.open('POST', '/clear_invitation');

    // When the request is loaded successfully
    request.onload = function() {
        // Extract JSON data from request
        const data = JSON.parse(request.responseText);
    };

    // Add data to send with request
    const data = new FormData();
    data.append("invitation_id", invitation.substring(1));

    // Send request
    request.send(data);
}