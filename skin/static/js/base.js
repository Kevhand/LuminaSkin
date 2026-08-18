function showToast(title, message, type = "success") {
    const container = document.getElementById("toast-container");
    if (!container) return;

    const toast = document.createElement("div");
    toast.className = "toast";

    // Check if the message is an error
    const isError = type.toLowerCase().includes("error");
    
    // Add the error class to trigger the red border in CSS
    if (isError) {
        toast.classList.add("error");
    }

    // Assign the appropriate icon
    const icon = isError ? "✕" : "✓";

    toast.innerHTML = `
        <h4>${icon} ${title}</h4>
        <p>${message}</p>
    `;

    container.appendChild(toast);

    // Trigger the slide-in animation
    requestAnimationFrame(() => {
        toast.classList.add("show");
    });

    // Handle the slide-out and removal
    setTimeout(() => {
        toast.classList.remove("show");

        // Wait for the CSS transition (0.4s) to finish before removing from DOM
        setTimeout(() => {
            toast.remove();
        }, 400); 

    }, 3500); // Display for 3.5 seconds
}