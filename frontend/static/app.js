document.addEventListener("DOMContentLoaded", () => {
    // Config: Backend Agent Decoupled API URL
    const BACKEND_API_URL = window.location.hostname === "localhost" ? "http://localhost:8000/api/chat" : "/api/chat";

    // DOM Elements
    const authScreen = document.getElementById("auth-screen");
    const chatScreen = document.getElementById("chat-screen");
    const tokenForm = document.getElementById("token-form");
    const tokenInput = document.getElementById("employee-token");
    const profileChips = document.querySelectorAll(".profile-chip");
    const btnSwitchToken = document.getElementById("btn-switch-token");
    
    const userNameDisplay = document.getElementById("user-name");
    const userRoleDisplay = document.getElementById("user-role");
    const userAvatarInitials = document.getElementById("user-avatar-initials");
    const activeTokenBadge = document.getElementById("active-token-badge");
    const tokenStatusFoot = document.getElementById("token-status-foot");
    
    const chatForm = document.getElementById("chat-form");
    const userInput = document.getElementById("user-input");
    const messagesContainer = document.getElementById("messages-container");
    const typingIndicator = document.getElementById("typing-indicator");
    const btnClearChat = document.getElementById("btn-clear-chat");
    const promptChips = document.querySelectorAll(".prompt-chip");

    // Current Session State
    let currentToken = "WW-10928";
    let currentUser = {
        name: "Alex Rivera",
        role: "Senior Cloud Developer",
        initials: "AR"
    };

    // Quick Profile Chips Click
    profileChips.forEach(chip => {
        chip.addEventListener("click", () => {
            profileChips.forEach(c => c.classList.remove("active"));
            chip.classList.add("active");
            tokenInput.value = chip.dataset.token;
        });
    });

    // Handle Token Login (Screen 1 -> Screen 2)
    tokenForm.addEventListener("submit", (e) => {
        e.preventDefault();
        const token = tokenInput.value.trim().toUpperCase();
        if (!token) return;

        currentToken = token;

        // Map Demo Profiles
        if (token === "WW-10928") {
            currentUser = { name: "Alex Rivera", role: "Senior Cloud Developer", initials: "AR" };
        } else if (token === "WW-88888") {
            currentUser = { name: "Sarah Chen", role: "Engineering Manager", initials: "SC" };
        } else {
            currentUser = { name: `Employee (${token})`, role: "Enterprise User", initials: token.substring(0, 2) };
        }

        // Update UI Displays
        userNameDisplay.textContent = currentUser.name;
        userRoleDisplay.textContent = currentUser.role;
        userAvatarInitials.textContent = currentUser.initials;
        activeTokenBadge.textContent = currentToken;
        tokenStatusFoot.textContent = `Token: ${currentToken}`;

        // Switch Screen
        authScreen.classList.add("hidden");
        chatScreen.classList.remove("hidden");
    });

    // Switch Token Back to Screen 1
    btnSwitchToken.addEventListener("click", () => {
        chatScreen.classList.add("hidden");
        authScreen.classList.remove("hidden");
    });

    // Clear Chat Conversation
    btnClearChat.addEventListener("click", () => {
        messagesContainer.innerHTML = `
            <div class="welcome-banner glass-panel">
                <div class="welcome-icon"><i class="fa-solid fa-handshake-angle"></i></div>
                <div class="welcome-text">
                    <h3>Conversation Reset</h3>
                    <p>Ready for your next HR or IT query.</p>
                </div>
            </div>
        `;
    });

    // Prompt Chips Click -> Trigger Query
    promptChips.forEach(chip => {
        chip.addEventListener("click", () => {
            const query = chip.dataset.query;
            if (query) {
                sendMessage(query);
            }
        });
    });

    // Submit Chat Form
    chatForm.addEventListener("submit", (e) => {
        e.preventDefault();
        const text = userInput.value.trim();
        if (!text) return;
        userInput.value = "";
        sendMessage(text);
    });

    // Send Message to Decoupled Backend Agent API
    async function sendMessage(userQuery) {
        // Append User Message Bubble
        appendMessage("user", userQuery);

        // Show Typing Indicator
        typingIndicator.classList.remove("hidden");
        messagesContainer.scrollTop = messagesContainer.scrollHeight;

        try {
            // Decoupled API Call passing Employee Token in Headers & Body
            const response = await fetch(BACKEND_API_URL, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "X-Employee-Token": currentToken
                },
                body: JSON.stringify({
                    query: userQuery,
                    employee_token: currentToken
                })
            });

            const data = await response.json();
            typingIndicator.classList.add("hidden");

            if (data.response_text) {
                appendAgentResponse(data);
            } else {
                appendMessage("agent", "Received empty response from agent service.");
            }
        } catch (error) {
            typingIndicator.classList.add("hidden");
            appendMessage("agent", `⚠️ **Connection Error:** Could not connect to backend agent service at \`${BACKEND_API_URL}\`. Please ensure the backend agent container is running.`);
        }
    }

    // Append Simple User Message
    function appendMessage(sender, text) {
        const row = document.createElement("div");
        row.className = `message-row ${sender}`;
        
        const avatar = document.createElement("div");
        avatar.className = "message-avatar";
        avatar.innerHTML = sender === "user" ? `<i class="fa-solid fa-user"></i>` : `<i class="fa-solid fa-robot"></i>`;

        const bubble = document.createElement("div");
        bubble.className = "message-bubble";
        bubble.innerHTML = window.marked ? marked.parse(text) : text;

        row.appendChild(avatar);
        row.appendChild(bubble);
        messagesContainer.appendChild(row);
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }

    // Append Full Agent Response with Citations & Warm Handoff Cards
    function appendAgentResponse(data) {
        const row = document.createElement("div");
        row.className = "message-row agent";
        
        const avatar = document.createElement("div");
        avatar.className = "message-avatar";
        avatar.innerHTML = `<i class="fa-solid fa-robot"></i>`;

        const bubble = document.createElement("div");
        bubble.className = "message-bubble";

        // Render Markdown Text
        let htmlContent = window.marked ? marked.parse(data.response_text) : data.response_text;

        // Render Source Citations if present
        if (data.citations && data.citations.length > 0) {
            htmlContent += `<div class="citation-box">`;
            htmlContent += `<div class="citation-title"><i class="fa-solid fa-link"></i> Verified Policy Citation:</div>`;
            data.citations.forEach(c => {
                htmlContent += `<div>📄 <strong>${c.document_name}</strong> (${c.section}) - <a class="citation-link" href="${c.url}" target="_blank">View Policy Document</a></div>`;
            });
            htmlContent += `</div>`;
        }

        // Render Warm Handoff Escalation Card if triggered
        if (data.warm_handoff_card) {
            const card = data.warm_handoff_card;
            htmlContent += `
                <div class="warm-handoff-card">
                    <div class="warm-handoff-title"><i class="fa-solid fa-headset"></i> Human Warm-Handoff Escalation Dispatched</div>
                    <div>Ticket Reference: <strong>${card.ticket_reference_id}</strong> (${card.category})</div>
                    <div>Expected SLA: <strong>${card.expected_sla}</strong></div>
                    <a href="${card.redirect_url}" class="btn-handoff" target="_blank">
                        <i class="fa-solid fa-comments"></i> Connect to Live Support Chat
                    </a>
                </div>
            `;
        }

        bubble.innerHTML = htmlContent;
        row.appendChild(avatar);
        row.appendChild(bubble);
        messagesContainer.appendChild(row);
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }
});
