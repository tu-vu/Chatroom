document.addEventListener("DOMContentLoaded", function() {
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
                button.innerHTML = channel_name;

                // Append the new li to list
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

        // Prevent form from submitting again
        return false;
    };

    document.querySelector("#send").onclick = function() {
        // Create new message tag
        const p = document.createElement('p');

        // Set content of message tag
        p.innerHTML = document.querySelector("#message").value;

        // Append new message to messages
        document.querySelector("#messages").append(p);

        // Adding delete button for each message
        const but = document.createElement('button');

        //set content of the button
        but.innerHTML = "[x]";

        // Append the button to the div
        document.querySelector("#messages").append(but);

        // Stop page from reloading
        return false;
    };

    document.querySelector("#messages").onclick = function(event) {

     let targetId = event.target;
     if(targetId.tagName != "BUTTON") return;

     remove(targetId);
    };

    function remove(target){
      let sibling = target.previousSibling;
      sibling.remove();
      target.remove();
    }
});