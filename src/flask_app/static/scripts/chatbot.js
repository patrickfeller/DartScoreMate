document.addEventListener('DOMContentLoaded', () => {
    const chatButton = document.createElement('button');
    chatButton.className = 'chat-button';
    chatButton.innerHTML = '<i class="fas fa-robot"></i>';
    document.body.appendChild(chatButton);

    const chatWindow = document.createElement('div');
    chatWindow.className = 'chat-window';
    chatWindow.innerHTML = `
        <div class="chat-header">
            <i class="fas fa-robot"></i>
            <span>Mrs. Darts - Ihre Dart-Expertin</span>
        </div>
        <div class="chat-messages"></div>
        <div class="chat-input">
            <input type="text" placeholder="Stellen Sie Ihre Frage...">
            <button>&#x27A4;</button>
        </div>
    `;
    document.body.appendChild(chatWindow);

    const messagesContainer = chatWindow.querySelector('.chat-messages');
    const input = chatWindow.querySelector('input');
    const sendButton = chatWindow.querySelector('button');

    // Chatfenster anzeigen/verstecken und Verlauf laden
    chatButton.addEventListener('click', async () => {
        chatWindow.classList.toggle('active');

        // Wenn geöffnet, lade den bisherigen Verlauf
        if (chatWindow.classList.contains('active')) {
            try {
                const res = await fetch('/chat_history');
                const history = await res.json();

                messagesContainer.innerHTML = ''; // leeren, um Duplikate zu vermeiden

                history.forEach(entry => {
                    addMessage(entry.user, true); // User Nachricht
                    addMessage(entry.bot, false); // Bot Antwort
                });
            } catch (err) {
                console.error("Fehler beim Laden des Chatverlaufs", err);
                addMessage('Fehler beim Laden des Chatverlaufs.');
            }
        }
    });

    // Funktion, um Nachrichten hinzuzufügen
    function addMessage(message, isUser = false) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${isUser ? 'user-message' : 'bot-message'}`;
        messageDiv.textContent = message;
        messagesContainer.appendChild(messageDiv);
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }

    // Nachricht senden
    async function sendMessage() {
        const message = input.value.trim();
        if (!message) return;

        addMessage(message, true);  // User Nachricht anzeigen
        input.value = '';

        try {
            const response = await fetch('/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ message: message })
            });

            const data = await response.json();
            if (data.error) {
                console.error('API Fehler:', data.error);
                console.error('Fehlertyp:', data.error_type);
                addMessage(`Entschuldigung, es gab einen Fehler: ${data.error}`);
            } else {
                addMessage(data.response, false); // Antwort des Bots anzeigen
            }
        } catch (error) {
            console.error('Netzwerkfehler:', error);
            addMessage('Entschuldigung, es gab einen Netzwerkfehler. Bitte überprüfen Sie Ihre Internetverbindung.');
        }
    }

    sendButton.addEventListener('click', sendMessage);
    input.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            sendMessage();
        }
    });

    // Willkommensnachricht
    addMessage('Hallo! Ich bin Mrs. Darts, Ihre persönliche Dart-Expertin. Wie kann ich Ihnen helfen?');
});
