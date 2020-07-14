document.addEventListener("DOMContentLoaded", function() {
    // Load all channels associating with user before DOM is loaded
    load_channels();

    // Set create button to disabled as default
    document.querySelector("#create").disabled = true;

    // When user type anything in input bar, enable create button
    document.querySelector("#channel_name").onkeyup = function() {
        // If input bar is not empty, enable button
        if (document.querySelector("#channel_name").value.length > 0) {
            document.querySelector("#create").disabled = false;
        } else {
            document.querySelector("#create").disabled = true;
        }
    };

    // Set create button to disabled as default
    document.querySelector("#send").disabled = true;

    // When user type anything in input bar, enable create button
    document.querySelector("#message").onkeyup = function() {
        // If input bar is not empty, enable button
        if (document.querySelector("#message").value.length > 0) {
            document.querySelector("#send").disabled = false;
        } else {
            document.querySelector("#send").disabled = true;
        }
    };

    // CREATE NEW CHANNEL
    document.querySelector("#new_channel").onsubmit = function() {
        // Initialize a new request
        const request = new XMLHttpRequest();
        request.open('POST', '/create');

        const channel_name = document.querySelector("#channel_name").value;

        // When the request is loaded successfully
        request.onload = function() {
            // Extract JSON data from request
            const data = JSON.parse(request.responseText);

            // If creation of new channel is successful
            if(data.success) {
                const button = document.createElement('button');
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
        // Create new message tag
        const p = document.createElement('p');

        // Set content of message tag
        p.innerHTML = document.querySelector("#message").value;

        // Append new message to messages
        document.querySelector("#messages").append(p);

        // Adding delete button for each message
        const button = document.createElement('button');

        //set content of the button
        button.innerHTML = "[x]";

        // Append the button to the div
        document.querySelector("#messages").append(button);

        // Stop page from reloading
        return false;
    };

    // WHEN USER CLICK ONE OF CHANNEL
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
        }
    };

    // REMOVE A MESSAGE
    document.querySelector("#messages").onclick = function(event) {
     let targetId = event.target;
     if(targetId.tagName != "BUTTON") return;

     remove(targetId);
    };
});

// LOAD EXISTING CHANNELS FOR USER
function load_channels() {
    // Initialize a new request
    const request = new XMLHttpRequest();
    request.open('GET', '/load');

    request.onload = function() {
        // Extract JSON data from object
        const data = JSON.parse(request.responseText);

        // Traverse and print all channels
        for (channel of data.channels) {
            // Create a button
            const button = document.createElement('button');
            button.className += "channel";
            button.innerHTML = channel;

            // Add button to field
            document.querySelector("#channels").append(button);
        }
    };

    // Send request
    request.send();

    return false;
}

// REMOVE A MESSAGE
function remove(target){
  let sibling = target.previousSibling;
  sibling.remove();
  target.remove();
}
