document.addEventListener('DOMContentLoaded', function() {
    const chatForm = document.getElementById('chat-form');
    const userInput = document.getElementById('user-input');
    const chatMessages = document.getElementById('chat-messages');

    // Function to add a message to the chat
    function addMessage(message, isUser = false) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${isUser ? 'user' : 'bot'}`;
        messageDiv.textContent = message;
        chatMessages.appendChild(messageDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    // Function to handle form submission
    async function handleSubmit(e) {
        e.preventDefault();
        const message = userInput.value.trim();
        
        if (!message) return;

        // Add user message to chat
        addMessage(message, true);
        userInput.value = '';

        try {
            // Send message to server
            const response = await fetch('/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    message: message,
                    mode: 'general'
                })
            });

            const data = await response.json();
            
            // Add bot response to chat
            if (data.response) {
                addMessage(data.response);
            }

            // If emergency contacts are included, display them
            if (data.emergency_contacts) {
                const emergencyMessage = document.createElement('div');
                emergencyMessage.className = 'message bot emergency';
                emergencyMessage.innerHTML = `
                    <strong>Emergency Contacts:</strong><br>
                    ${Object.entries(data.emergency_contacts)
                        .map(([service, number]) => `${service}: ${number}`)
                        .join('<br>')}
                `;
                chatMessages.appendChild(emergencyMessage);
                chatMessages.scrollTop = chatMessages.scrollHeight;
            }
        } catch (error) {
            console.error('Error:', error);
            addMessage('Sorry, I encountered an error. Please try again.');
        }
    }

    // Add event listener for form submission
    chatForm.addEventListener('submit', handleSubmit);

    // Add event listener for Enter key
    userInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            handleSubmit(e);
        }
    });
}); 