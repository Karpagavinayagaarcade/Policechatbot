document.addEventListener('DOMContentLoaded', function() {
    const chatForm = document.getElementById('kids-chat-form');
    const userInput = document.getElementById('kids-user-input');
    const chatMessages = document.getElementById('kids-chat-messages');

    // Kids mode specific responses
    const kidsResponses = {
        emergency: {
            keywords: ['emergency', 'help', 'danger', '911'],
            response: '🚨 Remember: If you need help, call 911! This number will connect you to police, fire, or ambulance services. Always tell them your name and where you are!'
        },
        safety: {
            keywords: ['safety', 'safe', 'danger', 'stranger'],
            response: '🛡️ Safety Tips:\n1. Always stay with a trusted adult\n2. Never talk to strangers\n3. Know your address and phone number\n4. If you feel unsafe, tell someone you trust!'
        },
        police: {
            keywords: ['police', 'officer', 'cop', 'law'],
            response: '👮 Police officers are your friends! They help keep everyone safe and protect our community. If you need help, you can always ask a police officer!'
        }
    };

    // Function to add a message to the chat
    function addMessage(message, isUser = false) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${isUser ? 'user' : 'bot'}`;
        messageDiv.textContent = message;
        chatMessages.appendChild(messageDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    // Function to check for emergency keywords
    function checkForEmergency(message) {
        const lowerMessage = message.toLowerCase();
        if (lowerMessage.includes('emergency') || lowerMessage.includes('help') || lowerMessage.includes('danger')) {
            return true;
        }
        return false;
    }

    // Function to get appropriate response based on keywords
    function getResponse(message) {
        const lowerMessage = message.toLowerCase();
        
        // Check for emergency first
        if (checkForEmergency(lowerMessage)) {
            return {
                response: kidsResponses.emergency.response,
                isEmergency: true
            };
        }

        // Check other keywords
        for (const [category, data] of Object.entries(kidsResponses)) {
            if (data.keywords.some(keyword => lowerMessage.includes(keyword))) {
                return {
                    response: data.response,
                    isEmergency: false
                };
            }
        }

        // Default response
        return {
            response: 'Hi there! 👋 I\'m your police friend! What would you like to learn about today? You can ask me about safety tips, emergency numbers, or anything else!',
            isEmergency: false
        };
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
            // Get response from server
            const response = await fetch('/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    message: message,
                    mode: 'kids'
                })
            });

            const data = await response.json();
            
            // Add bot response to chat
            if (data.response) {
                addMessage(data.response);
            }

            // If it's an emergency response, add extra emphasis
            if (data.isEmergency) {
                const emergencyMessage = document.createElement('div');
                emergencyMessage.className = 'message bot emergency';
                emergencyMessage.innerHTML = '🚨 <strong>Remember: In an emergency, call 911 immediately!</strong>';
                chatMessages.appendChild(emergencyMessage);
                chatMessages.scrollTop = chatMessages.scrollHeight;
            }
        } catch (error) {
            console.error('Error:', error);
            addMessage('Oops! Something went wrong. Please try again! 😊');
        }
    }

    // Function to show emergency info
    window.showEmergencyInfo = function() {
        addMessage(kidsResponses.emergency.response);
    };

    // Function to show safety tips
    window.showSafetyTips = function() {
        addMessage(kidsResponses.safety.response);
    };

    // Add event listener for form submission
    chatForm.addEventListener('submit', handleSubmit);

    // Add event listener for Enter key
    userInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            handleSubmit(e);
        }
    });
}); 