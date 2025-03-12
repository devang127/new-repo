function addEvent() {
    let eventName = document.getElementById("eventName").value;
    let eventDate = document.getElementById("eventDate").value;
    let messageBox = document.getElementById("message");

    if (!eventName || !eventDate) {
        messageBox.innerHTML = "⚠️ Please fill in all fields.";
        return;
    }

    fetch("http://127.0.0.1:5000/add_event", {  // Ensure Flask's correct port is used
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            event_name: eventName,
            event_date: eventDate
        })
    })
    .then(response => response.json())
    .then(data => {
        messageBox.innerHTML = "✅ " + data.message;
    })
    .catch(error => {
        console.error("Error:", error);
        messageBox.innerHTML = "❌ Failed to add event.";
    });
}
