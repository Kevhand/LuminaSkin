/* ==================================================
   LUMINASKIN GUIDED TOURS
   Standalone module — does not read/modify anything
   dashboard.js/profile.js own (charts, insights, trends,
   concern buttons, drag & drop, date-of-birth input).

   Independent tours, each with its own trigger condition
   and its own per-user storage key:
     1. PRE-SCAN     — brand-new users, never scanned before (dashboard).
     2. POST-SCAN    — right after the user's first result (dashboard).
     3. PROFILE      — first visit to the profile page.
================================================== */

(function () {

    // Bump any version if that tour's layout changes enough
    // that even users who've seen it should see it again.
    const PRE_TOUR_VERSION = "1";
    const POST_TOUR_VERSION = "1";
    const PROFILE_TOUR_VERSION = "1";
    const SKIN_PROFILE_TOUR_VERSION = "1";
    const CHAT_TOUR_VERSION = "1";

    // localStorage is scoped to the browser, not the logged-in account —
    // without a per-user suffix, "seen" on one account would incorrectly
    // hide a tour from a different account signing up on the same
    // browser. currentUserId is set once at startup from whichever page
    // marker element is present, and used to build every key below.
    let currentUserId = "anon";

    function getPreStorageKey() {
        return "luminaskin_prescan_tour_v" + PRE_TOUR_VERSION + "_user_" + currentUserId;
    }

    function getPostStorageKey() {
        return "luminaskin_postscan_tour_v" + POST_TOUR_VERSION + "_user_" + currentUserId;
    }

    function getProfileStorageKey() {
        return "luminaskin_profile_tour_v" + PROFILE_TOUR_VERSION + "_user_" + currentUserId;
    }

    function getSkinProfileStorageKey() {
        return "luminaskin_skinprofile_tour_v" + SKIN_PROFILE_TOUR_VERSION + "_user_" + currentUserId;
    }

    function getChatStorageKey() {
        return "luminaskin_chat_tour_v" + CHAT_TOUR_VERSION + "_user_" + currentUserId;
    }

    const PRE_SCAN_STEPS = [
        {
            selector: "#dropzone",
            title: "Step 1: Upload a Photo",
            text: "Drag a clear, front-facing photo here, or click to browse your files.",
            position: "right",
            buttonText: "Next"
        },
        {
            selector: "#concern-select-area",
            title: "Step 2: Pick What to Check",
            text: "Choose the skin concerns you'd like us to look at — eyes, texture, tone, whatever matters to you.",
            position: "right",
            buttonText: "Next"
        },
        {
            selector: "#analyze-skin-btn",
            title: "Step 3: Run Your Scan",
            text: "Hit Analyze Skin and we'll process your photo in a few seconds.",
            position: "top",
            buttonText: "Got it!"
        }
    ];

    const POST_SCAN_STEPS = [
        {
            selector: "#skin-summary-card",
            title: "Your Skin Snapshot",
            text: "This is your quick summary — overall score, skin age, and skin type at a glance.",
            position: "left",
            buttonText: "Next"
        },
        {
            selector: "#concern-buttons-list",
            title: "Explore Each Concern",
            text: "Tap any concern to see its individual score and details.",
            position: "bottom",
            buttonText: "Next"
        },
        {
            selector: "#analysis-image-overlay",
            title: "See It, Not Just a Number",
            text: "This overlay shows exactly where on your face this concern shows up.",
            position: "right",
            buttonText: "Next"
        },
        {
            selector: "#analytics-progress-section",
            title: "Track Your Progress",
            text: "Every future scan gets saved here, so you can watch your skin change over time.",
            position: "top",
            buttonText: "Next"
        },
        {
            selector: "#insights-section",
            title: "Guidance Made for You",
            text: "This scan is just the start — the more you share about your routine and goals, the smarter your guidance gets.",
            position: "top",
            buttonText: "Next"
        },
        {
            selector: "#nav-profile-link",
            title: "Personalize Your LuminaSkin Experience",
            text: "The more we know about you, the more personalized your recommendations can become. Your profile helps LuminaSkin understand things like your skin goals, age, country, budget, allergies, pregnancy status, and product preferences.\n\nYou don't need to fill everything out right away. Add information whenever you're comfortable.",
            position: "bottom",
            buttonText: "Next"
        },
        {
            selector: "#nav-chat-link",
            title: "Your AI Skincare Assistant",
            text: "Have questions about your skin? Talk to LuminaSkin AI to better understand your results, get skincare guidance, update your routine and products, or explore ways to improve your skin concerns.\n\nYou can come back to Chat anytime you want personalized help.",
            position: "bottom",
            buttonText: "Got it, let's go!"
        }
    ];

    const PROFILE_STEPS = [
        {
            selector: "#profile-edit-card",
            title: "Update Your Details",
            text: "Add your mobile number and date of birth here anytime — small details, but they help keep your account accurate.",
            position: "top",
            buttonText: "Next"
        },
        {
            selector: "#skin-profile-link",
            title: "Give LuminaSkin More Context",
            text: "Your scan tells us what your skin looks like right now. Your skin profile, lifestyle, routine, and products help us understand why it may be happening and what you can actually do about it.\n\nYou can add things like skin goals & allergies, sleep & water intake, stress levels, sun exposure & SPF, exercise habits, and your current routine & products.\n\nThe more you add, the better our AI chat can help with your skin concerns.",
            position: "right",
            buttonText: "Got it!"
        }
    ];

    const SKIN_PROFILE_STEPS = [
        {
            selector: '.tab_button[data-tab="basic_info"]',
            title: "Basic Information",
            text: "Your age, gender, country, budget, skin goals, and allergies — the basics that shape every recommendation we give you.",
            position: "bottom",
            buttonText: "Next"
        },
        {
            selector: '.tab_button[data-tab="lifestyle"]',
            title: "Lifestyle",
            text: "Sleep, water intake, stress, sun exposure, and exercise — daily habits that show up on your skin.",
            position: "bottom",
            buttonText: "Next"
        },
        {
            selector: '.tab_button[data-tab="routine"]',
            title: "Daily Routine",
            text: "Your morning and night routine, so we know what you're already doing before suggesting changes.",
            position: "bottom",
            buttonText: "Next"
        },
        {
            selector: '.tab_button[data-tab="products"]',
            title: "Products",
            text: "Log the products you use so we can track what's working and what might be causing breakouts.\n\nYou don't need to fill in every section right away — our AI works with whatever you provide. The more you add, the more personalized your guidance gets.",
            position: "bottom",
            buttonText: "Got it!"
        }
    ];

    const CHAT_STEPS = [
        {
            selector: "#chat-header",
            title: "Meet Your AI Skincare Assistant \u{1F916}",
            text: "Have questions about your skin? Just ask.\n\nLuminaSkin AI can help you understand your scan results, work through your skin concerns, and suggest ways to improve your routine based on what it knows about you.",
            position: "bottom",
            buttonText: "Next"
        },
        {
            selector: "#chat-messages-area",
            title: "Get Personalized Guidance \u2728",
            text: "Your AI knows more than just your scan.\n\nAs you add your skin goals, lifestyle, routine, products, and preferences, LuminaSkin can use that information to give you more relevant recommendations.",
            position: "bottom",
            buttonText: "Next"
        },
        {
            selector: "#chat-actions-row",
            title: "Update Your Details \u{1F4AC}",
            text: 'You don\'t always need to fill out a form. Just click the section you want to update and tell the AI what\'s changed.\n\n"I started using a new moisturizer." "I stopped smoking." "My goal is now to reduce dark circles."\n\nThe AI can update your profile, lifestyle, routine, and product information for you.',
            position: "top",
            buttonText: "Next"
        },
        {
            selector: "#input-area",
            title: "Keep Improving Your Skin \u{1F331}",
            text: "Your conversation can evolve with your skin.\n\nAsk follow-up questions, discuss your concerns, update your information, and get guidance that adapts as your skincare journey changes.",
            position: "top",
            buttonText: "Got it!"
        }
    ];

    /* ============ shared spotlight engine (used by both tours) ============ */

    let currentStepIndex = 0;
    let backdropEl = null;
    let tooltipEl = null;
    let resizeHandlerAttached = false;
    let activeSteps = [];
    let activeOnFinish = null;

    function isCompleted(storageKey) {
        try {
            return localStorage.getItem(storageKey) === "done";
        } catch (e) {
            return false;
        }
    }

    function markCompleted(storageKey) {
        try {
            localStorage.setItem(storageKey, "done");
        } catch (e) {
            /* no-op — storage unavailable, non-fatal */
        }
    }

    function getVisibleSteps(steps) {
        return steps.filter((step) => !!document.querySelector(step.selector));
    }

    function placeAroundTarget(target, step) {
        const rect = target.getBoundingClientRect();
        const padding = 8;

        backdropEl.style.top = (rect.top - padding) + "px";
        backdropEl.style.left = (rect.left - padding) + "px";
        backdropEl.style.width = (rect.width + padding * 2) + "px";
        backdropEl.style.height = (rect.height + padding * 2) + "px";

        // Measure the tooltip's actual rendered size (its content was
        // already set by renderStep before this runs) instead of guessing
        // a fixed width/height — text length varies per step and screen.
        const tooltipRect = tooltipEl.getBoundingClientRect();
        const tooltipWidth = tooltipRect.width || 300;
        const tooltipHeight = tooltipRect.height || 150;
        const gap = 16;

        let top, left;

        switch (step.position) {
            case "left":
                top = rect.top;
                left = rect.left - tooltipWidth - gap;
                break;
            case "right":
                top = rect.top;
                left = rect.right + gap;
                break;
            case "top":
                top = rect.top - tooltipHeight - gap;
                left = rect.left;
                break;
            case "bottom":
            default:
                top = rect.bottom + gap;
                left = rect.left;
                break;
        }

        const maxLeft = window.innerWidth - tooltipWidth - 16;
        const maxTop = window.innerHeight - tooltipHeight - 16;

        left = Math.max(16, Math.min(left, maxLeft));
        top = Math.max(16, Math.min(top, maxTop));

        tooltipEl.style.top = top + "px";
        tooltipEl.style.left = left + "px";
    }

    function positionElements(step) {
        const target = document.querySelector(step.selector);
        if (!target) return;

        // Scroll to the target FIRST, instantly ("auto", not "smooth") —
        // a smooth scroll is asynchronous, so measuring the target's
        // position before it finishes scrolling is what caused the
        // spotlight to land in the wrong place. Waiting one animation
        // frame after an instant scroll guarantees layout has settled
        // before anything gets measured.
        target.scrollIntoView({ behavior: "auto", block: "center" });

        requestAnimationFrame(() => {
            placeAroundTarget(target, step);
        });
    }

    function renderStep() {
        const step = activeSteps[currentStepIndex];
        if (!step) {
            endSpotlight();
            return;
        }

        const dotsHtml = activeSteps
            .map((_, i) => `<span class="tour_dot${i === currentStepIndex ? " active" : ""}"></span>`)
            .join("");

        tooltipEl.innerHTML = `
            <h4>${step.title}</h4>
            <p>${step.text}</p>
            <div class="tour_tooltip_footer">
                <div class="tour_dots">${dotsHtml}</div>
                <div class="tour_tooltip_actions">
                    <button type="button" class="tour_skip_link" id="tour-skip-btn">Skip</button>
                    <button type="button" class="tour_next_btn" id="tour-next-btn">${step.buttonText}</button>
                </div>
            </div>
        `;

        document.getElementById("tour-next-btn").addEventListener("click", () => {
            currentStepIndex += 1;
            if (currentStepIndex >= activeSteps.length) {
                endSpotlight();
            } else {
                // renderStep() sets the new tooltip content and then
                // positions everything against that new content's real
                // size — don't position here first, it would measure
                // against the previous step's stale tooltip.
                renderStep();
            }
        });

        document.getElementById("tour-skip-btn").addEventListener("click", endSpotlight);

        positionElements(step);
    }

    function runSpotlight(steps, onFinish) {
        activeSteps = getVisibleSteps(steps);
        activeOnFinish = onFinish;

        if (activeSteps.length === 0) {
            if (onFinish) onFinish();
            return;
        }

        currentStepIndex = 0;

        backdropEl = document.createElement("div");
        backdropEl.className = "tour_backdrop";
        document.body.appendChild(backdropEl);

        tooltipEl = document.createElement("div");
        tooltipEl.className = "tour_tooltip";
        document.body.appendChild(tooltipEl);

        renderStep();

        if (!resizeHandlerAttached) {
            window.addEventListener("resize", () => {
                if (backdropEl && tooltipEl && activeSteps[currentStepIndex]) {
                    positionElements(activeSteps[currentStepIndex]);
                }
            });
            resizeHandlerAttached = true;
        }
    }

    function endSpotlight() {
        if (backdropEl) {
            backdropEl.remove();
            backdropEl = null;
        }
        if (tooltipEl) {
            tooltipEl.remove();
            tooltipEl = null;
        }
        if (activeOnFinish) {
            const fn = activeOnFinish;
            activeOnFinish = null;
            fn();
        }
    }

    /* ============ post-scan flow ============ */

    function showReadyBanner(onDone) {
        const banner = document.createElement("div");
        banner.className = "tour_ready_banner";
        banner.textContent = "Your results are ready \u2728";
        document.body.appendChild(banner);

        requestAnimationFrame(() => banner.classList.add("visible"));

        setTimeout(() => {
            banner.classList.remove("visible");
            setTimeout(() => {
                banner.remove();
                onDone();
            }, 400);
        }, 1400);
    }

    function startPostScanTour() {
        runSpotlight(POST_SCAN_STEPS, () => markCompleted(getPostStorageKey()));
    }

    /* ============ profile flow ============ */

    function startProfileTour() {
        runSpotlight(PROFILE_STEPS, () => markCompleted(getProfileStorageKey()));
    }

    /* ============ skin profile (edit) flow ============ */

    function startSkinProfileTour() {
        runSpotlight(SKIN_PROFILE_STEPS, () => markCompleted(getSkinProfileStorageKey()));
    }

    /* ============ chat flow ============ */

    function startChatTour() {
        runSpotlight(CHAT_STEPS, () => markCompleted(getChatStorageKey()));
    }

    /* ============ pre-scan (welcome) flow ============ */

    function showWelcomeModal(onStart, onSkip) {
        const overlay = document.createElement("div");
        overlay.className = "tour_welcome_overlay";
        overlay.innerHTML = `
            <div class="tour_welcome_card">
                <h3>Welcome to LuminaSkin \u{1F44B}</h3>
                <p>Let's get your first skin scan started. We'll walk you through it in three quick steps.</p>
                <div class="tour_welcome_actions">
                    <button type="button" class="tour_skip_link" id="welcome-skip-btn">Skip</button>
                    <button type="button" class="tour_next_btn" id="welcome-start-btn">Show Me How</button>
                </div>
            </div>
        `;
        document.body.appendChild(overlay);

        document.getElementById("welcome-start-btn").addEventListener("click", () => {
            overlay.remove();
            onStart();
        });

        document.getElementById("welcome-skip-btn").addEventListener("click", () => {
            overlay.remove();
            onSkip();
        });
    }

    function startPreScanTour() {
        showWelcomeModal(
            () => runSpotlight(PRE_SCAN_STEPS, () => markCompleted(getPreStorageKey())),
            () => markCompleted(getPreStorageKey())
        );
    }

    /* ============ init ============ */

    function resolveUserId() {
        // Check every known page-marker element in turn — only one of
        // these will exist on any given page, but this keeps user-id
        // resolution in one place instead of duplicated per tour.
        const markerIds = ["dashboard-layout", "profile-layout", "edit-skin-profile-layout", "chat-page-layout"];
        for (const id of markerIds) {
            const el = document.getElementById(id);
            if (el) {
                const uid = el.getAttribute("data-user-id");
                if (uid) return uid;
            }
        }
        return "anon";
    }

    function initDashboardTours() {
        const dashboardEl = document.getElementById("dashboard-layout");
        const replayBtn = document.getElementById("replay-tour-btn");

        if (replayBtn) {
            // Manual replay always plays the results tour if results exist,
            // otherwise the getting-started tour.
            replayBtn.addEventListener("click", () => {
                const hasResults = dashboardEl && dashboardEl.getAttribute("data-has-results") === "true";
                if (hasResults) {
                    startPostScanTour();
                } else {
                    startPreScanTour();
                }
            });
        }

        if (!dashboardEl) return;

        const hasResults = dashboardEl.getAttribute("data-has-results") === "true";
        const totalScans = parseInt(dashboardEl.getAttribute("data-total-scans"), 10) || 0;

        if (hasResults) {
            // A scan result is showing right now.
            if (!isCompleted(getPostStorageKey())) {
                setTimeout(() => showReadyBanner(startPostScanTour), 400);
            }
            return;
        }

        // No result showing. Only treat this as a brand-new user if they
        // have zero scan history — a returning user who just hasn't
        // scanned this session should never see the "welcome" tour.
        if (totalScans === 0 && !isCompleted(getPreStorageKey())) {
            setTimeout(startPreScanTour, 400);
        }
    }

    function initProfileTour() {
        const profileEl = document.getElementById("profile-layout");
        if (!profileEl) return;

        if (!isCompleted(getProfileStorageKey())) {
            setTimeout(startProfileTour, 400);
        }
    }

    function initSkinProfileTour() {
        const skinProfileEl = document.getElementById("edit-skin-profile-layout");
        if (!skinProfileEl) return;

        if (!isCompleted(getSkinProfileStorageKey())) {
            setTimeout(startSkinProfileTour, 400);
        }
    }

    function initChatTour() {
        const chatEl = document.getElementById("chat-page-layout");
        if (!chatEl) return;

        if (!isCompleted(getChatStorageKey())) {
            setTimeout(startChatTour, 400);
        }
    }

    document.addEventListener("DOMContentLoaded", () => {
        currentUserId = resolveUserId();
        initDashboardTours();
        initProfileTour();
        initSkinProfileTour();
        initChatTour();
    });

})();