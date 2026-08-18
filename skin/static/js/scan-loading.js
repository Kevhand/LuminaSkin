/* ==================================================
   SCAN LOADING OVERLAY
   Standalone module — only listens to the scan upload
   form's submit event. Does not touch dashboard.js,
   tour.js, or any chart/insight rendering logic. Safe
   to remove this file entirely without affecting anything
   else on the page.
================================================== */

(function () {

    const LOADING_MESSAGES = [
        "Uploading your photo...",
        "Detecting skin type...",
        "Mapping your selected concerns...",
        "Analyzing texture and tone...",
        "Almost there..."
    ];

    const MESSAGE_INTERVAL_MS = 2200;

    let messageIndex = 0;
    let messageTimer = null;
    let messageEl = null;

    function cycleMessage() {
        if (!messageEl) return;

        messageEl.classList.add("fading");

        setTimeout(() => {
            messageIndex = (messageIndex + 1) % LOADING_MESSAGES.length;
            messageEl.textContent = LOADING_MESSAGES[messageIndex];
            messageEl.classList.remove("fading");
        }, 300);
    }

    function showOverlay() {
        const overlay = document.createElement("div");
        overlay.className = "scan_loading_overlay";
        overlay.innerHTML = `
            <div class="scan_loading_card">
                <div class="scan_loading_spinner"></div>
                <div class="scan_loading_message">${LOADING_MESSAGES[0]}</div>
                <div class="scan_loading_subtext">This can take up to a minute — please don't refresh or close this tab.</div>
            </div>
        `;
        document.body.appendChild(overlay);

        messageEl = overlay.querySelector(".scan_loading_message");
        messageIndex = 0;

        requestAnimationFrame(() => overlay.classList.add("visible"));

        messageTimer = setInterval(cycleMessage, MESSAGE_INTERVAL_MS);
    }

    document.addEventListener("DOMContentLoaded", () => {
        const form = document.getElementById("scan-form");
        const submitBtn = document.getElementById("analyze-skin-btn");
        if (!form) return;

        form.addEventListener("submit", (e) => {
            // Let the browser's own validation (required file input, etc.)
            // run first — if the form is invalid, this submit event never
            // fires, so we never show a loading overlay for a submission
            // that didn't actually happen.
            if (!form.checkValidity()) return;

            if (submitBtn) {
                submitBtn.disabled = true;
                submitBtn.textContent = "Analyzing...";
            }

            showOverlay();
        });
    });

})();