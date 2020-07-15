document.addEventListener("DOMContentLoaded", function() {
    // LOAD ALL CHANNELS ASSOCIATING WITH USER
    load_channels();

    // SET UP DEFAULT CONTENT FOR DASHBOARD(AKA WHEN NO CHANNEL IS SELECTED)
    document.querySelector("#messages").innerHTML = "<h3>Here is the dashboard, when no channel is selected</h3>";

    // DISABLE SUBMIT BUTTONS BY DEFAULT
    document.querySelectorAll("input[type='submit']").forEach(function(button) {
        button.disabled = true;
    });

    // ONLY ENABLE SUBMIT BUTTONS WHEN USER TYPE SOMETHING
    document.querySelectorAll("#channel_name, #message").forEach(function(input_bar) {
        input_bar.onkeyup = function() {
            // Retrieve submit button
            const button = document.querySelector(`#${input_bar.id} + input`);

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
        // Initialize a new request
        const request = new XMLHttpRequest();
        request.open('POST', '/add_channel');

        const channel_name = document.querySelector("#channel_name").value;

        // When the request is loaded successfully
        request.onload = function() {
            // Extract JSON data from request
            const data = JSON.parse(request.responseText);

            // If creation of new channel is successful
            if(data.success) {
                const button = document.createElement('button');
                button.id = channel_name;
                button.className += "channel";
                button.innerHTML = channel_name;

                // Append new button to list
                document.querySelector("#channels").append(button);
            } else {
                alert(`Sorry, channel ${channel_name} already exists`);
            }
        };

        // Add data to send with request
        const data = new FormData();
        data.append("channel_name", channel_name);

        // Send request
        request.send(data);

        // Stop page from reloading
        return false;
    };

    // SEND A NEW MESSAGE
    document.querySelector("#send").onclick = function() {
        // User can only send message while in a channel
        const active_channel = document.querySelector(".active");

        if (active_channel == null) {
            // User has made no selection for channel -> Display error message
            alert("Sorry, You must select a channel first!");
            return false;
        }

        // Retrieve message typed by user 
        const message = document.querySelector("#message").value;

        // Initialize a new request
        const request = new XMLHttpRequest();
        request.open("POST", "/add_message");

        // Callback function when request completes
        request.onload = function() {
            const data = JSON.parse(request.responseText);

            // Create new message tag
            const p = document.createElement('p');

            // Set content of message tag
            p.innerHTML = data.message;

            // Append new message to messages
            document.querySelector("#messages").append(p);

            // Adding delete button for each message
            const button = document.createElement('button');

            //set content of the button
            button.innerHTML = "[x]";

            // Append the button to the div
            document.querySelector("#messages").append(button);
        };

        // Add data to send with request
        const data = new FormData();
        data.append("message", message);
        data.append("channel_name", active_channel.id);   

        // Send request 
        request.send(data);

        // Stop page from reloading
        return false;
    };

    // USER CLICKED ONE OF CHANNEL
    document.querySelector("#channels").onclick = function(div_area) {
        // div_area.target is the clicked element!

        // Only apply change if user click another button
        if (div_area.target && div_area.target.nodeName == "BUTTON") {
            // Get currently clicked button
            const active_button = document.querySelector(".active");

            // No button is clicked yet
            if (active_button != null) {
                // Remove clicked status
                active_button.className = active_button.className.replace(" active", "");
            }

            // Set the clicked button to active until another button is clicked
            div_area.target.className += " active";

            // LOAD MESSAGE HISTORY OF A CHANNEL

            // Initialize a new request
            const request = new XMLHttpRequest();
            request.open("POST", "/load_messages")

            // Callback function when request completes
            request.onload = function() {
                const data = JSON.parse(request.responseText);

                document.querySelector("#messages").innerHTML = `<h3>Here is messages history for ${data.channel_name} </h3>`;

                for(message of data.messages) {
                    const p = document.createElement("p");

                    p.innerHTML = `Text: ${message.message} written by ${message.author} at ${message.timestamp}`;

                    document.querySelector("#messages").append(p);
                }
            };

            // Add data to send with request
            const data = new FormData();
            data.append("channel_name", div_area.target.id);

            // Send request 
            request.send(data);

            // Stop page from reloading
            return false;
        }
    };

    // REMOVE A MESSAGE
    document.querySelector("#messages").onclick = function(event) {
        let targetId = event.target;
        if(targetId.nodeName != "BUTTON") return;

        remove(targetId);
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
            // Create a button
            const button = document.createElement('button');
            button.id = channel_name
            button.className += "channel";
            button.innerHTML = channel_name;

            // Add button to field
            document.querySelector("#channels").append(button);
        }
    };

    // Send request
    request.send();
}

// REMOVE A MESSAGE
function remove(target){
  let sibling = target.previousSibling;
  sibling.remove();
  target.remove();
}
