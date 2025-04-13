async function sendMessage() {
    const input = document.getElementById("user-input");
    const chatBox = document.getElementById("chat-box");

    const message = input.value;
    chatBox.innerHTML += `<div><strong>You:</strong> ${message}</div>`;

    const res = await fetch("/api/chat/", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": getCookie("csrftoken")
        },
        body: JSON.stringify({ message: message })
    });

    const data = await res.json();
    chatBox.innerHTML += `<div><strong>Bot:</strong> ${data.reply}</div>`;
    input.value = "";
    chatBox.scrollTop = chatBox.scrollHeight;
}

// CSRF token helper
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== "") {
        const cookies = document.cookie.split(";");
        for (let cookie of cookies) {
            cookie = cookie.trim();
            if (cookie.substring(0, name.length + 1) === (name + "=")) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
