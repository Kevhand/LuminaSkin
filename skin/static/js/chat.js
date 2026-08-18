document.addEventListener("DOMContentLoaded", function () {
    const messagesContainer = document.getElementById("messages");
    const chatBody = document.querySelector(".chat-body");
    const currentSessionInput = document.getElementById("current-session-id");

    const sendButton = document.getElementById("send-btn");
    const messageInput = document.getElementById("message-input");
    const newChatButton = document.getElementById("new_chat_button");
    const chatList = document.getElementById("chat-list");

    const updateRoutineButton =
        document.getElementById("update-routine-button");

    const updateProductButton =
        document.getElementById("update-product-button");

    const updateLifestyleButton =
        document.getElementById("update-lifestyle-button");

    const updateProfileButton =
        document.getElementById("update-profile-button");


    let currentSessionId = null;
    let currentMode = "chat";


    // ==================================================
    // EVENT LISTENERS
    // ==================================================

    newChatButton.addEventListener("click", createNewChat);

    sendButton.addEventListener("click", sendMessage);

    updateRoutineButton.addEventListener(
        "click",
        startRoutineUpdate
    );

    updateProductButton.addEventListener(
        "click",
        startProductUpdate
    );

    updateLifestyleButton.addEventListener(
        "click",
        startLifestyleUpdate
    );

    updateProfileButton.addEventListener(
        "click",
        startProfileUpdate
    );


    // ==================================================
    // AUTO-RESIZE TEXTAREA
    // ==================================================

    messageInput.addEventListener("input", function () {
        this.style.height = "auto";
        this.style.height =
            Math.min(this.scrollHeight, 150) + "px";
    });


    // ==================================================
    // ENTER = SEND
    // SHIFT + ENTER = NEW LINE
    // ==================================================

    messageInput.addEventListener("keydown", function (event) {

        if (
            event.key === "Enter" &&
            !event.shiftKey
        ) {
            event.preventDefault();
            sendMessage();
        }

    });


    // ==================================================
    // PRODUCT UPDATE MODE
    // ==================================================

    function startProductUpdate() {

        currentMode = "product_update";

        messageInput.placeholder =
            "Type your product update (e.g., 'I started using a new vitamin C serum')...";

        renderMessage(
            "assistant",
            "Sure. Which skincare product would you like to update, and what has changed?"
        );

        messageInput.focus();
    }


    // ==================================================
    // ROUTINE UPDATE MODE
    // ==================================================

    function startRoutineUpdate() {

        currentMode = "routine_update";

        messageInput.placeholder =
            "Type your routine updates (e.g., 'I started using retinol')...";

        renderMessage(
            "assistant",
            "Sure. What has changed in your skincare routine recently?"
        );

        messageInput.focus();
    }


    // ==================================================
    // LIFESTYLE UPDATE MODE
    // ==================================================

    function startLifestyleUpdate() {

        currentMode = "lifestyle_update";

        messageInput.placeholder =
            "Type your lifestyle update (e.g., 'I've been sleeping 6 hours lately')...";

        renderMessage(
            "assistant",
            "Sure. What has changed about your lifestyle recently?"
        );

        messageInput.focus();
    }


    // ==================================================
    // PROFILE UPDATE MODE
    // ==================================================

    function startProfileUpdate() {

        currentMode = "profile_update";

        messageInput.placeholder =
            "Type your profile update (e.g., 'I'm 21 years old')...";

        renderMessage(
            "assistant",
            "Sure. What would you like to update about your profile?"
        );

        messageInput.focus();
    }


    // ==================================================
    // RESET MODE
    // ==================================================

    function resetChatMode() {

        currentMode = "chat";

        messageInput.placeholder =
            "Ask LuminaSkin anything...";

        messageInput.style.height = "auto";
    }


    // ==================================================
    // CHAT ITEM SETUP
    // ==================================================

    function setupChatItem(item) {

        item.addEventListener("click", () => {

            document
                .querySelectorAll(".chat-item")
                .forEach(i =>
                    i.classList.remove("active")
                );

            item.classList.add("active");

            // Reset mode when switching chats
            resetChatMode();

            loadChat(item.dataset.sessionId);
        });


        const deleteButton =
            item.querySelector(".delete-chat-btn");

        if (deleteButton) {

            deleteButton.addEventListener(
                "click",
                (event) => {

                    event.stopPropagation();

                    deleteChat(
                        item.dataset.sessionId,
                        item
                    );
                }
            );
        }
    }


    // ==================================================
    // INITIALIZATION
    // ==================================================

    document
        .querySelectorAll(".chat-item")
        .forEach(item => setupChatItem(item));


    const initialChatItems =
        document.querySelectorAll(".chat-item");


    if (initialChatItems.length > 0) {

        initialChatItems[0].click();

    } else {

        createNewChat();
    }


    // ==================================================
    // LOAD CHAT HISTORY
    // ==================================================

    async function loadChat(sessionId) {

        currentSessionId = sessionId;

        currentSessionInput.value =
            sessionId;

        try {

            const response = await fetch(
                `/chat/history/${sessionId}/`
            );

            if (!response.ok) {
                throw new Error(
                    "Failed to load chat."
                );
            }

            const data =
                await response.json();

            messagesContainer.innerHTML = "";

            data.messages.forEach(message => {

                renderMessage(
                    message.role,
                    message.content
                );

            });

        } catch (error) {

            console.error(
                "Failed to load chat:",
                error
            );
        }
    }


    // ==================================================
    // SEND MESSAGE
    // ==================================================

    async function sendMessage() {

        const message =
            messageInput.value.trim();


        if (
            !message ||
            !currentSessionId
        ) {
            return;
        }


        // Show user message immediately
        renderMessage(
            "user",
            message
        );


        // Reset input
        messageInput.value = "";

        messageInput.style.height =
            "auto";

        sendButton.disabled = true;


        const thinkingBubble =
            createThinkingBubble();


        try {

            const formData =
                new FormData();

            formData.append(
                "message",
                message
            );

            formData.append(
                "session_id",
                currentSessionId
            );

            formData.append(
                "mode",
                currentMode
            );


            const response = await fetch(
                "/chat/send/",
                {
                    method: "POST",

                    headers: {
                        "X-CSRFToken":
                            getCSRFToken()
                    },

                    body: formData
                }
            );


            const data =
                await response.json();


            if (!response.ok) {

                throw new Error(
                    data.error ||
                    "Failed to send message."
                );
            }


            thinkingBubble.remove();


            renderMessage(
                "assistant",
                data.response
            );


            // ==================================================
            // UPDATE CHAT TITLE
            // ==================================================

            if (data.title) {

                const chatItem =
                    document.querySelector(
                        `.chat-item[data-session-id="${currentSessionId}"]`
                    );

                if (chatItem) {

                    const titleElement =
                        chatItem.querySelector(
                            ".chat-title"
                        );

                    if (titleElement) {

                        titleElement.textContent =
                            data.title;
                    }
                }
            }


            // ==================================================
            // RESET MODE AFTER COMPLETED ACTION
            // ==================================================

            if (
                data.plan &&
                (
                    data.plan.action ===
                        "routine_update_confirmed" ||

                    data.plan.action ===
                        "routine_update_cancelled" ||

                    data.plan.action ===
                        "product_update_confirmed" ||

                    data.plan.action ===
                        "product_update_cancelled" ||

                    data.plan.action ===
                        "product_added" ||

                    data.plan.action ===
                        "lifestyle_update_confirmed" ||

                    data.plan.action ===
                        "lifestyle_update_cancelled" ||

                    data.plan.action ===
                        "profile_update_confirmed" ||

                    data.plan.action ===
                        "profile_update_cancelled"
                )
            ) {

                resetChatMode();
            }

        } catch (error) {

            thinkingBubble.remove();

            renderMessage(
                "assistant",
                error.message
            );

            console.error(
                "Failed to send message:",
                error
            );

        } finally {

            sendButton.disabled = false;

            messageInput.focus();
        }
    }


    // ==================================================
    // RENDER MESSAGE
    // ==================================================

    function formatText(text) {
        let formatted = text;

        // Escape HTML first
        formatted = formatted
            .replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;");

        // Headings
        formatted = formatted.replace(
            /^### (.*)$/gm,
            "<h4>$1</h4>"
        );

        formatted = formatted.replace(
            /^## (.*)$/gm,
            "<h3>$1</h3>"
        );

        formatted = formatted.replace(
            /^# (.*)$/gm,
            "<h2>$1</h2>"
        );

        // Bold
        formatted = formatted.replace(
            /\*\*(.*?)\*\*/g,
            "<strong>$1</strong>"
        );

        // Italic
        formatted = formatted.replace(
            /(?<!\*)\*([^*\n]+)\*(?!\*)/g,
            "<em>$1</em>"
        );

        // Horizontal rules
        formatted = formatted.replace(
            /^(?:---|\*\*\*)$/gm,
            "<hr>"
        );

        // Bullet points
        // Supports -, • and *
        formatted = formatted.replace(
            /^\s*[-•*] (.*)$/gm,
            "<li>$1</li>"
        );

        // Numbered lists
        formatted = formatted.replace(
            /^\s*\d+\. (.*)$/gm,
            "<li>$1</li>"
        );

        // Wrap consecutive list items
        formatted = formatted.replace(
            /((?:<li>.*?<\/li>\s*)+)/gs,
            "<ul>$1</ul>"
        );

        // New lines
        formatted = formatted.replace(
            /\n/g,
            "<br>"
        );

        return formatted;
    }


    function renderMessage(
        role,
        content
    ) {

        const wrapper =
            document.createElement("div");

        wrapper.classList.add(
            "message",
            role
        );


        const contentDiv =
            document.createElement("div");

        contentDiv.classList.add(
            "content"
        );


        contentDiv.innerHTML =
            formatText(content);


        wrapper.appendChild(
            contentDiv
        );

        messagesContainer.appendChild(
            wrapper
        );


        scrollToBottom();
    }


    // ==================================================
    // THINKING INDICATOR
    // ==================================================

    function createThinkingBubble() {

        const wrapper =
            document.createElement("div");

        wrapper.classList.add(
            "message",
            "assistant"
        );


        const content =
            document.createElement("div");

        content.classList.add(
            "content"
        );


        content.innerHTML =
            `<span style="opacity: 0.6;">Thinking...</span>`;


        wrapper.appendChild(
            content
        );

        messagesContainer.appendChild(
            wrapper
        );


        scrollToBottom();


        return wrapper;
    }


    // ==================================================
    // SCROLL
    // ==================================================

    function scrollToBottom() {

        if (chatBody) {

            chatBody.scrollTop =
                chatBody.scrollHeight;
        }
    }


    // ==================================================
    // DELETE CHAT
    // ==================================================

    async function deleteChat(
        sessionId,
        chatItem
    ) {

        if (
            !confirm(
                "Are you sure you want to delete this conversation?"
            )
        ) {
            return;
        }


        try {

            const formData =
                new FormData();

            formData.append(
                "session_id",
                sessionId
            );


            const response =
                await fetch(
                    "/chat/delete/",
                    {
                        method: "POST",

                        headers: {
                            "X-CSRFToken":
                                getCSRFToken()
                        },

                        body: formData
                    }
                );


            if (!response.ok) {

                throw new Error(
                    "Failed to delete chat."
                );
            }


            chatItem.remove();


            // If deleted chat was open
            if (
                currentSessionId ===
                sessionId
            ) {

                currentSessionId =
                    null;

                currentSessionInput.value =
                    "";

                messagesContainer.innerHTML =
                    "";


                const remainingChats =
                    document.querySelectorAll(
                        ".chat-item"
                    );


                if (
                    remainingChats.length > 0
                ) {

                    remainingChats[0].click();

                } else {

                    createNewChat();
                }
            }

        } catch (error) {

            console.error(
                "Failed to delete chat:",
                error
            );
        }
    }


    // ==================================================
    // CREATE NEW CHAT
    // ==================================================

    async function createNewChat() {

        try {

            const response =
                await fetch(
                    "/chat/new/",
                    {
                        method: "POST",

                        headers: {
                            "X-CSRFToken":
                                getCSRFToken()
                        }
                    }
                );


            if (!response.ok) {

                throw new Error(
                    "Unable to create chat."
                );
            }


            const data =
                await response.json();


            currentSessionId =
                data.session_id;

            currentSessionInput.value =
                data.session_id;


            resetChatMode();


            messagesContainer.innerHTML =
                "";


            document
                .querySelectorAll(".chat-item")
                .forEach(item =>
                    item.classList.remove(
                        "active"
                    )
                );


            const chatItem =
                document.createElement(
                    "div"
                );

            chatItem.classList.add(
                "chat-item",
                "active"
            );

            chatItem.dataset.sessionId =
                data.session_id;


            const title =
                document.createElement(
                    "span"
                );

            title.classList.add(
                "chat-title"
            );

            title.textContent =
                data.title;


            const deleteButton =
                document.createElement(
                    "button"
                );

            deleteButton.classList.add(
                "delete-chat-btn"
            );

            deleteButton.dataset.sessionId =
                data.session_id;

            deleteButton.type =
                "button";

            deleteButton.innerHTML =
                "×";


            chatItem.appendChild(
                title
            );

            chatItem.appendChild(
                deleteButton
            );


            setupChatItem(
                chatItem
            );

            chatList.prepend(
                chatItem
            );


            messageInput.focus();

        } catch (error) {

            console.error(
                "Failed to create chat:",
                error
            );
        }
    }


    // ==================================================
    // CSRF TOKEN
    // ==================================================

    function getCSRFToken() {

        return document.cookie
            .split("; ")
            .find(
                row =>
                    row.startsWith(
                        "csrftoken="
                    )
            )
            ?.split("=")[1];
    }

});