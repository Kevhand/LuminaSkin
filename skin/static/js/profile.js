document.addEventListener("DOMContentLoaded", function () {
    
    // Django automatically prefixes form IDs with "id_"
    const dobInput = document.getElementById("id_date_of_birth");

    if (dobInput) {
        // Change the input type from "text" to "date" to trigger the browser's native calendar
        dobInput.type = "date";
        
        // Optional UX improvement: Prevent users from selecting future dates
        const today = new Date().toISOString().split("T")[0];
        dobInput.max = today;
    }

});