document.addEventListener("DOMContentLoaded", function () {
    const tabButtons = document.querySelectorAll(".tab_button");
    const tabContents = document.querySelectorAll(".tab_content");

    // Safety check in case the script loads on a page without tabs
    if (tabButtons.length === 0 || tabContents.length === 0) return;

    // ==================================================
    // 1. TAB SWITCHING LOGIC
    // ==================================================
    function switchTab(tabId) {
        const targetBtn = document.querySelector(`[data-tab="${tabId}"]`);
        const targetContent = document.getElementById(tabId);

        if (!targetBtn || !targetContent) return;

        // Reset all buttons and contents
        tabButtons.forEach(btn => {
            btn.classList.remove("active");
            btn.setAttribute("aria-selected", "false"); // Accessibility
        });
        
        tabContents.forEach(tab => {
            tab.classList.remove("active");
        });

        // Activate the selected tab
        targetBtn.classList.add("active");
        targetBtn.setAttribute("aria-selected", "true"); // Accessibility
        targetContent.classList.add("active");

        // Save state to survive page reloads (form submissions)
        localStorage.setItem("activeProfileTab", tabId);
    }

    // ==================================================
    // 2. INITIALIZATION & EVENT LISTENERS
    // ==================================================
    
    // Set up accessibility roles and click events
    tabButtons.forEach(btn => {
        btn.setAttribute("role", "tab");
        btn.setAttribute("aria-selected", btn.classList.contains("active") ? "true" : "false");
        
        btn.addEventListener("click", () => switchTab(btn.dataset.tab));
    });

    tabContents.forEach(tab => {
        tab.setAttribute("role", "tabpanel");
    });

    // ==================================================
    // 3. RESTORE SAVED STATE
    // ==================================================
    const savedTab = localStorage.getItem("activeProfileTab");
    
    if (savedTab) {
        switchTab(savedTab);
    }
});