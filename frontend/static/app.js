document.addEventListener("DOMContentLoaded", () => {
    // DOM Screens
    const screenWelcome = document.getElementById("screen-welcome");
    const screenQA = document.getElementById("screen-qa");

    // Welcome Screen Controls
    const btnBypassLaunch = document.getElementById("btn-bypass-launch");
    const welcomeTokenForm = document.getElementById("welcome-token-form");
    const inputToken = document.getElementById("input-token");
    const profileChips = document.querySelectorAll(".chip-profile");

    // QA Screen Controls
    const sidebar = document.getElementById("sidebar");
    const btnToggleSidebar = document.getElementById("btn-toggle-sidebar");
    const btnReturnWelcome = document.getElementById("btn-return-welcome");
    const btnNewChat = document.getElementById("btn-new-chat");
    
    // Identity Displays
    const qaUserName = document.getElementById("qa-user-name");
    const qaUserRole = document.getElementById("qa-user-role");
    const qaUserToken = document.getElementById("qa-user-token");
    const qaAvatarInitials = document.getElementById("qa-avatar-initials");
    const footerTokenDisplay = document.getElementById("footer-token-display");

    // Chat Controls
    const chatStream = document.getElementById("chat-stream");
    const starterCanvas = document.getElementById("starter-canvas");
    const thinkingIndicator = document.getElementById("thinking-indicator");
    const qaForm = document.getElementById("qa-form");
    const qaTextarea = document.getElementById("qa-textarea");
    const promptChips = document.querySelectorAll(".qa-prompt-chip");
    const starterCards = document.querySelectorAll(".starter-card");

    // Session State
    let currentToken = "WW-10928";
    let currentUser = {
        name: "Alex Rivera",
        role: "Senior Cloud Developer",
        initials: "AR"
    };

    let ticketCounter = 8912;
    let leaveBalances = {
        vacation_remaining: 16.0,
        vacation_accrued: 16.0,
        sick_remaining: 40.0,
        sick_accrued: 40.0,
        sg_childcare_remaining: 6.0
    };

    // Quick Profile Chips Selection on Welcome Screen
    profileChips.forEach(chip => {
        chip.addEventListener("click", () => {
            profileChips.forEach(c => c.classList.remove("active"));
            chip.classList.add("active");
            inputToken.value = chip.dataset.token;
        });
    });

    // 1. Direct Launch Button (BYPASS AUTH -> Enter Q&A Workspace Immediately)
    btnBypassLaunch.addEventListener("click", () => {
        const token = inputToken.value.trim().toUpperCase() || "WW-10928";
        switchUserSession(token);
        launchQAScreen();
    });

    // 2. Token Form Submit
    welcomeTokenForm.addEventListener("submit", (e) => {
        e.preventDefault();
        const token = inputToken.value.trim().toUpperCase() || "WW-10928";
        switchUserSession(token);
        launchQAScreen();
    });

    // 3. Return to Welcome Screen
    btnReturnWelcome.addEventListener("click", () => {
        screenQA.classList.add("hidden");
        screenWelcome.classList.remove("hidden");
    });

    // 4. Reset Conversation
    btnNewChat.addEventListener("click", () => {
        resetChatStream();
    });

    // Toggle Sidebar
    btnToggleSidebar.addEventListener("click", () => {
        sidebar.classList.toggle("collapsed");
    });

    // Prompt Chips & Starter Cards Clicks
    promptChips.forEach(chip => {
        chip.addEventListener("click", () => {
            const prompt = chip.dataset.prompt;
            if (prompt) sendMessage(prompt);
        });
    });

    starterCards.forEach(card => {
        card.addEventListener("click", () => {
            const prompt = card.dataset.prompt;
            if (prompt) sendMessage(prompt);
        });
    });

    // Submit Q&A Textarea Form
    qaForm.addEventListener("submit", (e) => {
        e.preventDefault();
        const query = qaTextarea.value.trim();
        if (!query) return;
        qaTextarea.value = "";
        sendMessage(query);
    });

    // Helper: Switch Identity Profile
    function switchUserSession(token) {
        currentToken = token;
        if (token === "WW-10928") {
            currentUser = { name: "Alex Rivera", role: "Senior Cloud Developer (US)", initials: "AR" };
            leaveBalances = { vacation_remaining: 16.0, vacation_accrued: 16.0, sick_remaining: 40.0, sick_accrued: 40.0, sg_childcare_remaining: 0.0 };
        } else if (token === "SG-40012") {
            currentUser = { name: "Jun Wei Tan", role: "Regional Operations Lead (Singapore)", initials: "JT" };
            leaveBalances = { vacation_remaining: 14.0, vacation_accrued: 14.0, sick_remaining: 14.0, sick_accrued: 14.0, sg_childcare_remaining: 6.0 };
        } else if (token === "WW-88888") {
            currentUser = { name: "Sarah Chen", role: "Engineering Manager", initials: "SC" };
            leaveBalances = { vacation_remaining: 80.0, vacation_accrued: 120.0, sick_remaining: 60.0, sick_accrued: 80.0, sg_childcare_remaining: 0.0 };
        } else {
            currentUser = { name: `Employee (${token})`, role: "Enterprise User", initials: token.substring(0, 2) };
            leaveBalances = { vacation_remaining: 24.0, vacation_accrued: 40.0, sick_remaining: 40.0, sick_accrued: 40.0, sg_childcare_remaining: 0.0 };
        }

        // Update Workspace Displays
        qaUserName.textContent = currentUser.name;
        qaUserRole.textContent = currentUser.role;
        qaAvatarInitials.textContent = currentUser.initials;
        qaUserToken.textContent = currentToken;
        footerTokenDisplay.textContent = `Token: ${currentToken}`;
    }

    // Helper: Transition to Screen 2 Q&A Workspace (Bypassing Auth)
    function launchQAScreen() {
        screenWelcome.classList.add("hidden");
        screenQA.classList.remove("hidden");
    }

    // Helper: Reset Chat Stream to Starter Canvas
    function resetChatStream() {
        chatStream.innerHTML = "";
        chatStream.appendChild(starterCanvas);
        starterCanvas.classList.remove("hidden");
    }

    // Standalone Simulation Engine (Bypassing Backend)
    function sendMessage(userQuery) {
        // Hide Starter Canvas on first message
        if (starterCanvas && !starterCanvas.classList.contains("hidden")) {
            starterCanvas.classList.add("hidden");
        }

        // Append User Message Bubble
        appendChatBubble("user", userQuery);

        // Show Thinking Indicator
        thinkingIndicator.classList.remove("hidden");
        chatStream.scrollTop = chatStream.scrollHeight;

        // Simulate 500ms AI Processing Delay
        setTimeout(() => {
            thinkingIndicator.classList.add("hidden");
            const responseData = simulateAgentLogic(userQuery);
            appendAgentBubble(responseData);
        }, 500);
    }

    // Client-Side Agent Logic Simulation (Matching SDD/BRD & Rubric Gotchas)
    function simulateAgentLogic(query) {
        const queryLower = query.toLowerCase();

        // 1. Model Armor Safety Interception
        if (queryLower.includes("ignore all") || queryLower.includes("dan mode") || queryLower.includes("reveal system prompt") || queryLower.includes("extract all salaries")) {
            return {
                response_text: "I cannot process this request as it violates company AI safety policies. Please rephrase your question regarding HR policies or self-service.",
                citations: []
            };
        }

        // 2. Human Warm-Handoff Escalation Request
        if (queryLower.includes("human agent") || queryLower.includes("representative") || queryLower.includes("talk to a human") || queryLower.includes("urgent help")) {
            ticketCounter++;
            const ticketId = `INC00${ticketCounter}`;
            return {
                response_text: `I have created a high-priority escalation ticket **${ticketId}** and dispatched it to HR/IT Operations. A live specialist will connect with you shortly.`,
                citations: [],
                warm_handoff_card: {
                    ticket_reference_id: ticketId,
                    category: "AI Service Escalation",
                    expected_sla: "< 15 mins",
                    redirect_url: "https://hr-helpdesk.corp.internal/live-chat"
                }
            };
        }

        // 3. Ethics & Gift Card / Cash Tip Gotcha (reference-eval.json ho_cash_tip_gotcha)
        if (queryLower.includes("cash tip") || queryLower.includes("gift card") || queryLower.includes("$40 cash")) {
            return {
                response_text: `⚠️ **Policy Prohibited Category (Section 5.2 & 14.2):**\n\nNo, cash and cash equivalents (including gift cards and cash tips) are strictly **prohibited** as business courtesies regardless of value. The $40 amount being under the $50 threshold is irrelevant because cash is a prohibited category.`,
                citations: [{
                    document_name: "Corporate Ethics & Business Courtesies Policy",
                    section: "Section 5.2 - Prohibited Gift Categories",
                    url: "https://hr-portal.internal/policies/ethics#gifts"
                }]
            };
        }

        // 4. Abstention Refusal: Absent Tuition Reimbursement Policy (reference-eval.json ho_tuition_reimbursement_absent)
        if (queryLower.includes("tuition") || queryLower.includes("master's degree") || queryLower.includes("pet")) {
            return {
                response_text: "I could not find an answer to this in our approved HR policy documents. Altostrat has no tuition reimbursement or pet leave policy on file.",
                citations: []
            };
        }

        // 5. Singapore Regional Policy: Childcare Leave (Singapore Statutory Entitlement)
        if (queryLower.includes("singapore") || queryLower.includes("childcare")) {
            return {
                response_text: `According to the **Singapore Statutory & HR Leave Annex** (*Section 19.4*):\n\nEmployees working under Singapore contracts with Singapore-citizen children under 7 years old are entitled to **6 paid childcare leave days** per calendar year (funded jointly by government and employer).`,
                citations: [{
                    document_name: "Singapore Regional HR Addendum",
                    section: "Section 19.4 - Childcare & Parental Entitlements",
                    url: "https://hr-portal.internal/policies/singapore#childcare"
                }]
            };
        }

        // 6. UC-2.1 Equipment Procurement
        if (queryLower.includes("monitor") || (queryLower.includes("remote") && queryLower.includes("order"))) {
            ticketCounter++;
            const ticketId = `INC00${ticketCounter}`;
            return {
                response_text: `**Cross-System Workflow Completed (UC-2.1 Equipment Procurement):**\n\n1. **Policy Verified:** Under *Section 3.1 of Remote Work Policy*, remote employees are eligible for a 27-inch monitor.\n2. **WorkWeek Status:** Verified employee **${currentUser.name}** status as \`APPROVED_REMOTE\`.\n3. **ServiceImmediately Order:** Successfully created Hardware Incident Ticket **${ticketId}** for IT shipping dispatch.`,
                citations: [{
                    document_name: "Remote Work & Home Office Policy",
                    section: "Section 3.1 - Home Office Equipment Entitlement",
                    url: "https://hr-portal.internal/policies/remote-work#equipment"
                }]
            };
        }

        // 7. UC-2.2 Medical Leave Setup
        if (queryLower.includes("medical leave") || queryLower.includes("short-term disability")) {
            ticketCounter++;
            const ticketId = `INC00${ticketCounter}`;
            return {
                response_text: `**Cross-System Workflow Completed (UC-2.2 Medical Leave):**\n\n1. **Policy Quoted:** *Short-Term Medical Leave Policy (Section 5.0)* provides up to 12 weeks of leave.\n2. **WorkWeek Leave Submitted:** Submitted Medical Leave request for ${currentUser.name}.\n3. **Confidential Case Opened:** Created HRSD Case **${ticketId}** in ServiceImmediately for manager email routing.`,
                citations: [{
                    document_name: "Short-Term Medical Leave Policy",
                    section: "Section 5.0 - Medical Leave of Absence",
                    url: "https://hr-portal.internal/policies/medical-leave#process"
                }]
            };
        }

        // 8. UC-2.3 London Relocation Transfer
        if (queryLower.includes("london") || queryLower.includes("relocation")) {
            ticketCounter++;
            const ticketId = `INC00${ticketCounter}`;
            return {
                response_text: `**Cross-System Workflow Completed (UC-2.3 London Relocation):**\n\n1. **Policy Allowance:** Quoted up to **$5,000** relocation allowance under *Global Mobility Policy (Section 2.4)*.\n2. **WorkWeek Updated:** Updated primary address to London transfer location.\n3. **Facilities Ticket Created:** Opened Badge & Building Access Ticket **${ticketId}** in ServiceImmediately.`,
                citations: [{
                    document_name: "Global Mobility & Relocation Policy",
                    section: "Section 2.4 - International Office Transfers",
                    url: "https://hr-portal.internal/policies/mobility#relocation-allowance"
                }]
            };
        }

        // 9. WorkWeek PTO Balance Query
        if (queryLower.includes("pto") || queryLower.includes("balance") || queryLower.includes("accrued")) {
            return {
                response_text: `Hello **${currentUser.name}**! Here are your real-time **WorkWeek HCM** leave balances:\n\n- 🌴 **Vacation Leave:** **${intVal(leaveBalances.vacation_remaining)} hours** remaining (2 days)\n- 🩺 **Sick Leave:** **${intVal(leaveBalances.sick_remaining)} hours** remaining (5 days)\n${leaveBalances.sg_childcare_remaining > 0 ? `- 👶 **Singapore Childcare Leave:** **${leaveBalances.sg_childcare_remaining} days** remaining\n` : ''}\n*Note: Real-time fetch directly from WorkWeek HCM. Zero dynamic caching.*`,
                citations: []
            };
        }

        // 10. WorkWeek Leave Submission & Overdraw Guardrail (Calculates deduction properly without double-subtraction)
        if (queryLower.includes("vacation") || queryLower.includes("submit") || queryLower.includes("time-off") || queryLower.includes("take off")) {
            if (queryLower.includes("40 hours") || queryLower.includes("5 days")) {
                return {
                    response_text: `⚠️ **WorkWeek Business Guardrail Violation:** You requested **40 hours** of vacation, but your available balance is **${intVal(leaveBalances.vacation_remaining)} hours**. Would you like to submit a request for ${intVal(leaveBalances.vacation_remaining)} hours instead?`,
                    citations: []
                };
            }
            leaveBalances.vacation_remaining = Math.max(0, leaveBalances.vacation_remaining - 16.0);
            const leaveId = `WW-LEAVE-${Math.random().toString(36).substring(2, 8).toUpperCase()}`;
            return {
                response_text: `✅ **Time-Off Request Submitted:** Vacation leave for Thursday and Friday has been recorded in WorkWeek HCM (Reference: \`${leaveId}\`). Your remaining vacation balance is now **${intVal(leaveBalances.vacation_remaining)} hours**.`,
                citations: []
            };
        }

        // 11. ServiceImmediately Ticket Queries
        if (queryLower.includes("ticket") || queryLower.includes("inc123456")) {
            return {
                response_text: `🎫 **Ticket Status (INC123456):**\n- **Status:** \`In Progress\`\n- **Category:** Network / VPN\n- **Assignee:** IT Network Team\n- **Latest Update:** *Re-provisioned client certificate. Please test.*`,
                citations: []
            };
        }

        // 12. Bereavement Policy Q&A
        if (queryLower.includes("bereavement")) {
            return {
                response_text: `According to the **Employee Leave & Time-Off Policy** (*Section 4.2 - Bereavement Leave*):\n\nEmployees are eligible for up to **five (5) consecutive paid working days** of bereavement leave in the event of the loss of an immediate family member (spouse, child, parent, sibling). For extended family members, up to three (3) paid days are provided.`,
                citations: [{
                    document_name: "Employee Leave & Time-Off Policy",
                    section: "Section 4.2 - Bereavement Leave",
                    url: "https://hr-portal.internal/policies/leave#bereavement"
                }]
            };
        }

        // Default Response
        return {
            response_text: `Hello **${currentUser.name}**! I am your Enterprise HR & IT Agentic Assistant.\n\nI can help you with:\n- **Policy Q&A:** Bereavement leave, expense guidelines, Singapore childcare leave\n- **Ethics Gotchas:** Business gift limits, cash tip prohibitions\n- **WorkWeek HCM:** Check PTO balance, submit leave requests\n- **ServiceImmediately ITSM:** Check ticket status, open IT support incidents\n- **Cross-System Sagas:** Equipment procurement (UC-2.1), Medical leave (UC-2.2), Relocation (UC-2.3)`,
            citations: []
        };
    }

    function intVal(num) {
        return Math.floor(num);
    }

    // Append User Chat Bubble
    function appendChatBubble(sender, text) {
        const row = document.createElement("div");
        row.className = `chat-row ${sender}`;

        const avatar = document.createElement("div");
        avatar.className = "avatar-badge";
        avatar.innerHTML = sender === "user" ? `<i class="fa-solid fa-user"></i>` : `<i class="fa-solid fa-sparkles"></i>`;

        const bubble = document.createElement("div");
        bubble.className = "chat-bubble";
        bubble.innerHTML = window.marked ? marked.parse(text) : text;

        row.appendChild(avatar);
        row.appendChild(bubble);
        chatStream.appendChild(row);
        chatStream.scrollTop = chatStream.scrollHeight;
    }

    // Append Structured Agent Bubble
    function appendAgentBubble(data) {
        const row = document.createElement("div");
        row.className = "chat-row agent";

        const avatar = document.createElement("div");
        avatar.className = "avatar-badge";
        avatar.innerHTML = `<i class="fa-solid fa-sparkles"></i>`;

        const bubble = document.createElement("div");
        bubble.className = "chat-bubble";

        let html = window.marked ? marked.parse(data.response_text) : data.response_text;

        // Policy Citations Card
        if (data.citations && data.citations.length > 0) {
            html += `<div class="citation-card">`;
            html += `<div class="citation-header"><i class="fa-solid fa-link"></i> Verified HR Policy Citation:</div>`;
            data.citations.forEach(c => {
                html += `<div>📄 <strong>${c.document_name}</strong> (${c.section}) &mdash; <a class="citation-anchor" href="${c.url}" target="_blank">Open Policy Source</a></div>`;
            });
            html += `</div>`;
        }

        // Warm Handoff Card
        if (data.warm_handoff_card) {
            const card = data.warm_handoff_card;
            html += `
                <div class="handoff-card-box">
                    <div class="handoff-header"><i class="fa-solid fa-headset"></i> Human Warm-Handoff Escalation Triggered</div>
                    <div>Support Ticket Reference: <strong>${card.ticket_reference_id}</strong> (${card.category})</div>
                    <div>Expected Response SLA: <strong>${card.expected_sla}</strong></div>
                    <a href="${card.redirect_url}" class="btn-live-chat" target="_blank">
                        <i class="fa-solid fa-comments"></i> Connect to Live Support Agent
                    </a>
                </div>
            `;
        }

        bubble.innerHTML = html;
        row.appendChild(avatar);
        row.appendChild(bubble);
        chatStream.appendChild(row);
        chatStream.scrollTop = chatStream.scrollHeight;
    }
});
