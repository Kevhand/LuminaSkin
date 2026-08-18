/* ==================================================
   0. DRAG & DROP UPLOAD
================================================== */
document.addEventListener("DOMContentLoaded", () => {
    const dropzone = document.getElementById("dropzone");
    const fileInput = document.getElementById("image");
    const dropText = document.querySelector(".drop_text");

    if (dropzone && fileInput) {
        // Highlight on drag
        ['dragenter', 'dragover'].forEach(eventName => {
            dropzone.addEventListener(eventName, preventDefaults, false);
            dropzone.addEventListener(eventName, () => dropzone.classList.add('dragover'), false);
        });

        // Remove highlight on leave
        ['dragleave', 'drop'].forEach(eventName => {
            dropzone.addEventListener(eventName, preventDefaults, false);
            dropzone.addEventListener(eventName, () => dropzone.classList.remove('dragover'), false);
        });

        // Handle file drop
        dropzone.addEventListener('drop', (e) => {
            fileInput.files = e.dataTransfer.files;
            handleFiles();
        }, false);
        
        // Handle normal click
        fileInput.addEventListener('change', handleFiles, false);
    }

    function preventDefaults(e) {
        e.preventDefault();
        e.stopPropagation();
    }

    function handleFiles() {
        if (fileInput.files && fileInput.files.length > 0) {
            dropzone.classList.add('has-file');
            if (dropText) {
                dropText.textContent = `File selected: ${fileInput.files[0].name}`;
            }
        }
    }
});



/* ==================================================
   1. UI INTERACTIONS (Concern Buttons & Overlays)
================================================== */

const buttons = document.querySelectorAll(".concern_button");

const overlayImage = document.getElementById("overlay_image");
const concernTitle = document.getElementById("selected_concern");
const score = document.getElementById("selected_score");





buttons.forEach(button => {

    button.addEventListener("click", () => {

        // Remove active state from all
        buttons.forEach(btn => btn.classList.remove("active"));

        // Add active state to clicked
        button.classList.add("active");

        // Update Viewer & Info
        if (overlayImage)
            overlayImage.src = button.dataset.overlay;

        if (concernTitle)
            concernTitle.textContent = formatConcernName(button.dataset.type);

        if (score)
            score.textContent = button.dataset.score;

    });

});


/* Initialize first button as active on load */

if (buttons.length > 0) {
    buttons[0].click();
}



/* ==================================================
   2. DATA PARSING
================================================== */

const parseJSONSafely = (id) => {

    const el = document.getElementById(id);

    return el
        ? JSON.parse(el.textContent)
        : null;

};


const graphs = parseJSONSafely("graph-data");
const summary = parseJSONSafely("summary-data");
const insights = parseJSONSafely("insights-data");
const trends = parseJSONSafely("trends-data");



/* ==================================================
   3. CHART.JS GLOBAL CONFIGURATION (Premium Theme)
================================================== */

// Custom Sage Green Theme Colors

const themeColors = {

    primary: '#4a7c73',

    primaryLight:
        'rgba(74, 124, 115, 0.2)',

    primaryFaded:
        'rgba(74, 124, 115, 0.05)',

    gridLine:
        '#e2e8f0',

    textMain:
        '#1e293b'

};


// Global Font Family

Chart.defaults.font.family =
    "'Inter', -apple-system, BlinkMacSystemFont, sans-serif";

Chart.defaults.color =
    themeColors.textMain;


// Reusable function to create beautiful gradient fills under lines

const createGradient = (ctx) => {

    const gradient =
        ctx.createLinearGradient(
            0,
            0,
            0,
            300
        );

    gradient.addColorStop(
        0,
        themeColors.primaryLight
    );

    gradient.addColorStop(
        1,
        themeColors.primaryFaded
    );

    return gradient;

};



/* ==================================================
   4. DATE FORMATTER
================================================== */

const formatDateLabel = (dateString) => {

    const date = new Date(dateString);

    return date.toLocaleDateString("en-IN", {

        day: "numeric",

        month: "short"

    });

};



/* ==================================================
   5. STANDARD CHART OPTIONS
================================================== */

const commonChartOptions = {

    responsive: true,

    maintainAspectRatio: false,

    plugins: {

        legend: {
            display: false
        },

        tooltip: {

            backgroundColor:
                'rgba(30, 41, 59, 0.9)',

            padding: 12,

            titleFont: {
                size: 13,
                weight: '600'
            },

            bodyFont: {
                size: 13
            },

            displayColors: false,

            cornerRadius: 8

        }

    },

    scales: {

        x: {

            grid: {
                display: false,
                drawBorder: false
            }

        },

        y: {

            beginAtZero: false,

            grid: {
                color: themeColors.gridLine,
                drawBorder: false
            },

            border: {
                display: false
            }

        }

    },

    interaction: {

        intersect: false,

        mode: 'index'

    }

};



/* ==================================================
   6. MAIN CHARTS (Overall Score & Skin Age)
================================================== */

const renderChart = (
    canvasId,
    label,
    chartData
) => {

    const canvas =
        document.getElementById(canvasId);

    if (!canvas)
        return;

    if (
        !chartData ||
        !chartData.values ||
        chartData.values.length === 0
    ) {
        // No data at all for this chart yet — replace the blank canvas
        // area with a friendly note instead of leaving it empty.
        const container = canvas.closest(".chart_container");
        if (container) {
            const note = document.createElement("p");
            note.className = "analytics_empty_note";
            note.textContent = "Scan again to start tracking this over time.";
            container.appendChild(note);
        }
        return;
    }


    const ctx =
        canvas.getContext('2d');


    new Chart(ctx, {

        type: "line",

        data: {

            labels:
                chartData.labels.map(
                    formatDateLabel
                ),

            datasets: [{

                label: label,

                data:
                    chartData.values,

                tension: 0.4,

                borderColor:
                    themeColors.primary,

                backgroundColor:
                    createGradient(ctx),

                borderWidth: 3,

                pointBackgroundColor:
                    '#ffffff',

                pointBorderColor:
                    themeColors.primary,

                pointBorderWidth: 2,

                pointRadius: 4,

                pointHoverRadius: 6,

                fill: true

            }]

        },

        options:
            commonChartOptions

    });

    // A first-ever scan means a single data point — the chart still
    // renders fine as one dot, just add a small note so it reads as
    // "expected" rather than "broken".
    if (chartData.values.length < 2) {
        const graphCard = canvas.closest(".graph_card");
        if (graphCard) {
            const note = document.createElement("p");
            note.className = "chart_single_point_note";
            note.textContent = "You have 1 scan so far — trends will appear after your next scan.";
            graphCard.appendChild(note);
        }
    }

};


if (graphs) {

    renderChart(
        "overall-score-chart",
        "Overall Score",
        graphs.overall_score
    );

    renderChart(
        "skin-age-chart",
        "Skin Age",
        graphs.skin_age
    );

}



/* ==================================================
   7. DYNAMIC CONCERN CHARTS
================================================== */

const formatConcernName = (concern) => {

    const names = {

        "dark_circle_v2":
            "Dark Circles",

        "eye_bag":
            "Eye Bags",

        "droopy_upper_eyelid":
            "Droopy Upper Eyelid",

        "droopy_lower_eyelid":
            "Droopy Lower Eyelid",

        "tear_trough":
            "Tear Trough",

        "acne":
            "Acne",

        "wrinkle":
            "Wrinkles",

        "firmness":
            "Firmness",

        "pore":
            "Pores",

        "redness":
            "Redness",

        "age_spot":
            "Age Spots",

        "oiliness":
            "Oiliness"

    };

    return names[concern] || concern;

};


const concernChartsContainer =
    document.getElementById(
        "concern-charts"
    );


if (
    concernChartsContainer &&
    graphs &&
    graphs.concerns &&
    Object.keys(graphs.concerns).length > 0
) {

    Object.entries(
        graphs.concerns
    ).forEach(
        ([concern, concernData]) => {

            // Build DOM elements for the grid

            const card =
                document.createElement("div");

            card.classList.add(
                "concern_chart_card"
            );


            const title =
                document.createElement("h4");

            title.textContent =
                formatConcernName(concern);


            const chartWrapper =
                document.createElement("div");

            chartWrapper.classList.add(
                "chart_container"
            );


            const canvas =
                document.createElement("canvas");


            chartWrapper.appendChild(
                canvas
            );

            card.appendChild(
                title
            );

            card.appendChild(
                chartWrapper
            );

            concernChartsContainer.appendChild(
                card
            );


            // Render chart instance

            const ctx =
                canvas.getContext('2d');


            new Chart(ctx, {

                type: "line",

                data: {

                    labels:
                        concernData.ui_score.labels.map(
                            formatDateLabel
                        ),

                    datasets: [{

                        label:
                            formatConcernName(
                                concern
                            ),

                        data:
                            concernData.ui_score.values,

                        tension: 0.4,

                        borderColor:
                            themeColors.primary,

                        backgroundColor:
                            createGradient(ctx),

                        borderWidth: 2,

                        pointRadius: 3,

                        pointHoverRadius: 5,

                        fill: true

                    }]

                },

                options:
                    commonChartOptions

            });

            // A first-ever scan means one data point per concern —
            // still renders fine as a single dot, just add a small note
            // so it doesn't look broken/incomplete.
            if (
                concernData.ui_score.values &&
                concernData.ui_score.values.length < 2
            ) {
                const note = document.createElement("p");
                note.className = "chart_single_point_note";
                note.textContent = "Scan again to start tracking this concern over time.";
                card.appendChild(note);
            }

        }
    );

} else if (concernChartsContainer) {

    // No concern history yet at all (e.g. very first scan) — show a
    // friendly placeholder instead of leaving this section blank.
    const note = document.createElement("p");
    note.className = "analytics_empty_note";
    note.textContent = "Your concern progress will show up here once you scan again.";
    concernChartsContainer.appendChild(note);

}



/* ==================================================
   8. HELPER FORMATTERS FOR TEXT DATA
================================================== */

const formatChange = (change) => {

    if (
        change === null ||
        change === undefined ||
        change === 0
    ) {
        return "";
    }

    return change > 0
        ? `+${change}`
        : `${change}`;

};


const formatDirection = (direction) => {

    if (direction === "improving")
        return "Improving";

    if (direction === "worsening")
        return "Worsening";

    if (direction === "stable")
        return "Stable";

    return direction;

};



/* ==================================================
   9. RENDER INSIGHTS
================================================== */

const insightsContainer =
    document.getElementById(
        "insights-container"
    );


if (
    insightsContainer &&
    insights
) {

    const {
        progress = {},
        concerns,
        consistency = {},
        highlights = {}
    } = insights;


    const createInsightItem =
        (title, value) => {

            const item =
                document.createElement("div");

            item.classList.add(
                "insight_item"
            );

            item.innerHTML = `
                <strong>${title}</strong>
                <span>${value}</span>
            `;

            return item;

        };


    /* Overall Progress */

    if (progress.overall_direction) {

        insightsContainer.appendChild(

            createInsightItem(

                "Overall Skin Score",

                `
                ${formatDirection(
                    progress.overall_direction
                )}

                ${formatChange(
                    progress.overall_change
                )}
                `

            )

        );

    }


    /* Skin Age */

    if (progress.skin_age_direction) {

        insightsContainer.appendChild(

            createInsightItem(

                "Skin Age",

                `
                ${formatDirection(
                    progress.skin_age_direction
                )}

                ${formatChange(
                    progress.skin_age_change
                )}
                `

            )

        );

    }


    /* Best Improvement */

    if (highlights.best_improvement) {

        insightsContainer.appendChild(

            createInsightItem(

                "Best Improvement",

                `
                ${formatConcernName(
                    highlights
                        .best_improvement
                        .concern
                )}

                improved by

                ${highlights
                    .best_improvement
                    .percent_change}%
                `

            )

        );

    }


    /* Largest Decline */

    if (highlights.largest_decline) {

        insightsContainer.appendChild(

            createInsightItem(

                "Needs Attention",

                `
                ${formatConcernName(
                    highlights
                        .largest_decline
                        .concern
                )}

                changed by

                ${highlights
                    .largest_decline
                    .percent_change}%
                `

            )

        );

    }


    /* Scan Consistency */

    if (
        consistency.total_scans !== null &&
        consistency.total_scans !== undefined
    ) {

        insightsContainer.appendChild(

            createInsightItem(

                "Scan Consistency",

                `
                ${consistency.total_scans}
                scans recorded
                `

            )

        );

    }


    /* Concern Groupings */

    if (concerns) {

        const concernCard =
            document.createElement("div");

        concernCard.classList.add(
            "insight_item"
        );

        // A first-ever scan has nothing to compare against yet, so the
        // backend may omit these arrays entirely — default to empty
        // instead of crashing on .length of undefined.
        const improved = concerns.improved || [];
        const worsened = concerns.worsened || [];
        const stable = concerns.stable || [];

        let html =
            "<strong>Concern Progress</strong>";


        /* Improving */

        if (
            improved.length > 0
        ) {

            html += `

                <div
                    class="concern_group improved"
                >

                    <span>
                        Improving
                    </span>

                    <p>
                        ${
                            improved
                                .map(formatConcernName)
                                .join(", ")
                        }
                    </p>

                </div>

            `;

        }


        /* Worsening */

        if (
            worsened.length > 0
        ) {

            html += `

                <div
                    class="concern_group worsened"
                >

                    <span>
                        Needs Attention
                    </span>

                    <p>
                        ${
                            worsened
                                .map(formatConcernName)
                                .join(", ")
                        }
                    </p>

                </div>

            `;

        }


        /* Stable */

        if (
            stable.length > 0
        ) {

            html += `

                <div
                    class="concern_group stable"
                >

                    <span>
                        Stable
                    </span>

                    <p>
                        ${
                            stable
                                .map(formatConcernName)
                                .join(", ")
                        }
                    </p>

                </div>

            `;

        }


        concernCard.innerHTML =
            html;

        insightsContainer.appendChild(
            concernCard
        );

    }

    // First-ever scan (or otherwise not enough history) means none of
    // the sections above had anything to add — show a friendly note
    // instead of leaving the whole Insights card blank.
    if (insightsContainer.children.length === 0) {
        const note = document.createElement("p");
        note.className = "analytics_empty_note";
        note.textContent = "Your personalized insights will appear here after your next scan.";
        insightsContainer.appendChild(note);
    }

}



/* ==================================================
   10. RENDER TRENDS
================================================== */

const trendsContainer =
    document.getElementById(
        "trends-container"
    );


if (
    trendsContainer &&
    trends
) {

    const renderTrendItem =
        (
            name,
            current,
            direction,
            change,
            percent_change
        ) => {

            const item =
                document.createElement("div");

            item.classList.add(
                "trend_item"
            );


            const formattedChange =
                formatChange(change);


            const percent =
                percent_change !== null &&
                percent_change !== undefined

                    ? `(
                        ${formatChange(
                            Number(
                                percent_change.toFixed(1)
                            )
                        )}%
                    )`

                    : "";


            item.innerHTML = `

                <div>

                    <strong>
                        ${name}
                    </strong>

                    <span>
                        ${current}
                    </span>

                </div>


                <div class="trend_status">

                    ${formatDirection(
                        direction
                    )}

                    ${formattedChange}

                    ${percent}

                </div>

            `;


            trendsContainer.appendChild(
                item
            );

        };


    /* Main Metrics */

    if (trends.overall_score) {

        renderTrendItem(

            "Overall Skin Score",

            trends.overall_score.current,

            trends.overall_score.direction,

            trends.overall_score.change,

            trends.overall_score.percent_change

        );

    }


    if (trends.skin_age) {

        renderTrendItem(

            "Skin Age",

            trends.skin_age.current,

            trends.skin_age.direction,

            trends.skin_age.change,

            trends.skin_age.percent_change

        );

    }


    /* Individual Concern Trends */

    if (trends.concerns) {

        Object.entries(
            trends.concerns
        ).forEach(
            ([concern, data]) => {

                const trend =
                    data.ui_score;

                if (trend) {

                    renderTrendItem(

                        formatConcernName(
                            concern
                        ),

                        trend.current,

                        trend.direction,

                        trend.change,

                        trend.percent_change

                    );

                }

            }
        );

    }

    // No comparable history yet (e.g. first-ever scan) — the sections
    // above had nothing to render — show a friendly note instead of
    // leaving the whole Trends card blank.
    if (trendsContainer.children.length === 0) {
        const note = document.createElement("p");
        note.className = "analytics_empty_note";
        note.textContent = "No changes to show yet — come back after your next scan to see what's changed.";
        trendsContainer.appendChild(note);
    }

}