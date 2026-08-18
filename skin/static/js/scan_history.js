document.addEventListener("DOMContentLoaded", () => {

    const deleteButtons =
        document.querySelectorAll(".delete-scan-btn");

    deleteButtons.forEach(button => {

        button.addEventListener("click", async () => {

            const deleteUrl =
                button.dataset.deleteUrl;

            if (!deleteUrl) {
                console.error("Delete URL is missing.");
                return;
            }

            const confirmed = confirm(
                "Are you sure you want to delete this scan?\n\n" +
                "This will permanently delete the scan and its analysis results."
            );

            if (!confirmed) {
                return;
            }

            try {

                const response = await fetch(
                    deleteUrl,
                    {
                        method: "POST",

                        headers: {
                            "X-CSRFToken": getCSRFToken(),
                        },
                    }
                );

                if (!response.ok) {
                    throw new Error(
                        "Failed to delete the scan."
                    );
                }

                // Remove the scan from the timeline immediately
                const timelineItem =
                    button.closest(".timeline_item");

                if (timelineItem) {
                    timelineItem.remove();
                }

                // If this was the last scan,
                // reload so Django renders the empty state.
                const remainingScans =
                    document.querySelectorAll(".timeline_item");

                if (remainingScans.length === 0) {
                    window.location.reload();
                }

            } catch (error) {

                console.error(
                    "Failed to delete scan:",
                    error
                );

                alert(
                    "We couldn't delete this scan. Please try again."
                );
            }

        });

    });

});


function getCSRFToken() {

    const csrfInput =
        document.querySelector(
            "[name=csrfmiddlewaretoken]"
        );

    return csrfInput
        ? csrfInput.value
        : "";
}