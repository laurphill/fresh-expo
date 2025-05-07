const chatForm = document.getElementById('chat-form');
const chatMessages = document.querySelector('.chat-messages');

// Get username and room from URL
const { username, room } = Qs.parse(location.search, {
    ignoreQueryPrefix: true,
});

// Display room name in sidebar
if (!room) {
    document.getElementById('room-name').innerText = 'No Room Selected';
} else {
    document.getElementById('room-name').innerText = room;
}


// Connect to Socket.io
const socket = io();

// Join chatroom
socket.emit('joinRoom', { username, room });

// Listen for messages from server
socket.on('message', (message) => {
    console.log(message); // For debugging
    outputMessage(message);
});

// Send message on form submit
chatForm.addEventListener('submit', (e) => {
    e.preventDefault();

    // Get message text
    const msg = e.target.elements.msg.value.trim();

    if (!msg) return; // Prevent sending empty messages

    // Emit message to server
    socket.emit('chatMessage', { room, msg });


    // Clear input
    e.target.elements.msg.value = '';
    e.target.elements.msg.focus();
});

// Output message to chat box
function outputMessage(message) {
    const div = document.createElement("div");

    // Add the common message class
    div.classList.add("message");

    // Check if this message is from the current user
    if (message.username === username) {
        div.classList.add("sent");
    } else {
        div.classList.add("received");
    }

    div.innerHTML = `
        <p class="meta">${message.username} <span>${message.time}</span></p>
        <p class="text">${message.message}</p>
    `;
    chatMessages.appendChild(div);

    // Scroll down to the latest message
    chatMessages.scrollTop = chatMessages.scrollHeight;
}
