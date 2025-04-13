async function sendMessage() {
    const input = document.getElementById("user-input");
    const chatBox = document.getElementById("chat-box");

    const message = input.value.trim();
    if (!message) return;

    chatBox.innerHTML += `<div><strong>You:</strong> ${message}</div>`;

    try {
        const res = await fetch("/chat/api/chat/", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": getCookie("csrftoken")
            },
            body: JSON.stringify({ message: message })
        });
    
        const contentType = res.headers.get("content-type");
        if (!contentType || !contentType.includes("application/json")) {
            throw new Error("Expected JSON, got something else");
        }
    
        const data = await res.json();
    
        if (data.reply) {
            chatBox.innerHTML += `<div><strong>Bot:</strong> ${data.reply}</div>`;
        } else {
            chatBox.innerHTML += `<div style="color: red;"><strong>Error:</strong> ${data.error}</div>`;
        }
    } catch (error) {
        chatBox.innerHTML += `<div style="color: red;"><strong>Error:</strong> ${error.message}</div>`;
        console.error("Chat error:", error);
    }
    

    input.value = "";
    chatBox.scrollTop = chatBox.scrollHeight;
}

// Helper for CSRF token
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
