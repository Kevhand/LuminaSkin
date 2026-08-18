import os
from io import BytesIO

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    Image,
    PageBreak,
)

from .charts import create_line_chart


def format_date(date_string):

    if not date_string:
        return "-"

    try:
        from datetime import datetime

        date = datetime.fromisoformat(
            date_string
        )

        return date.strftime(
            "%d %b %Y"
        )

    except (ValueError, TypeError):

        return str(date_string)


def format_concern_name(concern):

    names = {

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
            "Oiliness",
    }

    return names.get(
        concern,
        concern.replace("_", " ").title()
    )


def format_value(value, default="-"):

    if value is None:
        return default

    return str(value)


def format_percent(value):
    if value is None:
        return ""

    return f" ({value:.1f}%)"


def add_no_data_note(story, normal_style, text):
    story.append(
        Paragraph(
            f'<i><font color="#64748b">{text}</font></i>',
            normal_style
        )
    )
    story.append(Spacer(1, 8))


def build_pdf(report_data):
    chart_files = []
    buffer = BytesIO()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=18 * mm,
        leftMargin=18 * mm,
        topMargin=18 * mm,
        bottomMargin=22 * mm,
    )

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        "ReportTitle",
        parent=styles["Title"],
        alignment=TA_CENTER,
        fontSize=24,
        textColor=colors.HexColor("#4a7c73"),
        spaceAfter=8,
    )

    subtitle_style = ParagraphStyle(
        "Subtitle",
        parent=styles["Normal"],
        alignment=TA_CENTER,
        fontSize=11,
        textColor=colors.grey,
        spaceAfter=20,
    )

    heading_style = ParagraphStyle(
        "ReportHeading",
        parent=styles["Heading2"],
        fontSize=16,
        textColor=colors.HexColor("#1e293b"),
        spaceBefore=12,
        spaceAfter=10,
    )

    normal_style = ParagraphStyle(
        "ReportNormal",
        parent=styles["Normal"],
        fontSize=10,
        leading=14,
    )

    story = []

    summary = report_data.get(
        "summary",
        {}
    )

    insights = report_data.get(
        "insights",
        {}
    )

    graphs = report_data.get(
        "graphs",
        {}
    )

    trends = report_data.get(
        "trends",
        {}
    )


    # ==================================================
    # HEADER
    # ==================================================

    story.append(
        Paragraph(
            "LuminaSkin",
            title_style
        )
    )

    story.append(
        Paragraph(
            "Personal Skin Analysis Report",
            subtitle_style
        )
    )

    story.append(
        Paragraph(
            f"Latest Scan: "
            f"{format_date(summary.get('latest_scan_date'))}",
            subtitle_style
        )
    )

    story.append(Spacer(1, 8))


    # ==================================================
    # SUMMARY
    # ==================================================

    story.append(
        Paragraph(
            "Skin Summary",
            heading_style
        )
    )

    summary_data = [

        [
            "Total Scans",
            "Latest Score",
            "Skin Age",
            "Concerns Tracked",
        ],

        [
            format_value(summary.get("total_scans")),
            format_value(summary.get("latest_overall_score")),
            format_value(summary.get("latest_skin_age")),
            format_value(summary.get("concerns_tracked")),
        ],

    ]

    summary_table = Table(
        summary_data,
        colWidths=[
            42 * mm,
            42 * mm,
            42 * mm,
            42 * mm,
        ]
    )

    summary_table.setStyle(
        TableStyle([

            (
                "BACKGROUND",
                (0, 0),
                (-1, 0),
                colors.HexColor("#4a7c73")
            ),

            (
                "TEXTCOLOR",
                (0, 0),
                (-1, 0),
                colors.white
            ),

            (
                "ALIGN",
                (0, 0),
                (-1, -1),
                "CENTER"
            ),

            (
                "FONTNAME",
                (0, 0),
                (-1, 0),
                "Helvetica-Bold"
            ),

            (
                "FONTNAME",
                (0, 1),
                (-1, 1),
                "Helvetica-Bold"
            ),

            (
                "FONTSIZE",
                (0, 0),
                (-1, 0),
                9.5
            ),

            (
                "FONTSIZE",
                (0, 1),
                (-1, 1),
                14
            ),

            (
                "TEXTCOLOR",
                (0, 1),
                (-1, 1),
                colors.HexColor("#4a7c73")
            ),

            (
                "TOPPADDING",
                (0, 0),
                (-1, -1),
                10
            ),

            (
                "BOTTOMPADDING",
                (0, 0),
                (-1, -1),
                10
            ),

            (
                "GRID",
                (0, 0),
                (-1, -1),
                0.5,
                colors.HexColor("#e2e8f0")
            ),

            (
                "ROWBACKGROUNDS",
                (0, 1),
                (-1, 1),
                [colors.HexColor("#f0f7f5")]
            ),

        ])
    )

    story.append(
        summary_table
    )

    story.append(Spacer(1, 15))


    # ==================================================
    # OVERALL SCORE
    # ==================================================

    story.append(
        Paragraph(
            "Overall Score Progress",
            heading_style
        )
    )

    chart_path = create_line_chart(
        graphs.get(
            "overall_score",
            {}
        ),
        "Overall Skin Score",
        "Score"
    )

    if chart_path:

        chart_files.append(chart_path)

        story.append(
            Image(
                chart_path,
                width=165 * mm,
                height=72 * mm
            )
        )

    else:

        add_no_data_note(
            story,
            normal_style,
            "Not enough data yet — scan again to start tracking your overall score over time."
        )


    # ==================================================
    # SKIN AGE
    # ==================================================

    story.append(
        Paragraph(
            "Skin Age Progress",
            heading_style
        )
    )

    chart_path = create_line_chart(
        graphs.get(
            "skin_age",
            {}
        ),
        "Skin Age",
        "Age"
    )

    if chart_path:

        chart_files.append(chart_path)

        story.append(
            Image(
                chart_path,
                width=165 * mm,
                height=72 * mm
            )
        )

    else:

        add_no_data_note(
            story,
            normal_style,
            "Not enough data yet — scan again to start tracking your skin age over time."
        )


    story.append(
        PageBreak()
    )


    # ==================================================
    # CONCERN PROGRESS
    # ==================================================

    story.append(
        Paragraph(
            "Concern Progress",
            heading_style
        )
    )

    concerns = graphs.get(
        "concerns",
        {}
    )

    if not concerns:

        add_no_data_note(
            story,
            normal_style,
            "Your concern progress will show up here once you scan again."
        )

    for concern, data in concerns.items():

        story.append(
            Paragraph(
                format_concern_name(
                    concern
                ),
                styles["Heading3"]
            )
        )

        chart_path = create_line_chart(
            data.get(
                "ui_score",
                {}
            ),
            format_concern_name(
                concern
            ),
            "Score"
        )

        if chart_path:

            chart_files.append(chart_path)

            story.append(
                Image(
                    chart_path,
                    width=165 * mm,
                    height=65 * mm
                )
            )

        else:

            add_no_data_note(
                story,
                normal_style,
                "Scan again to start tracking this concern over time."
            )

        story.append(
            Spacer(1, 8)
        )


    # ==================================================
    # INSIGHTS
    # ==================================================

    story.append(
        PageBreak()
    )

    story.append(
        Paragraph(
            "Insights",
            heading_style
        )
    )

    progress = insights.get(
        "progress",
        {}
    )

    consistency = insights.get(
        "consistency",
        {}
    )

    highlights = insights.get(
        "highlights",
        {}
    )

    insight_rows = []


    if progress.get(
        "overall_direction"
    ):

        insight_rows.append([
            "Overall Score",
            progress.get(
                "overall_direction"
            ).title()
        ])


    if progress.get(
        "skin_age_direction"
    ):

        insight_rows.append([
            "Skin Age",
            progress.get(
                "skin_age_direction"
            ).title()
        ])


    if highlights.get(
        "best_improvement"
    ):

        best = highlights[
            "best_improvement"
        ]

        insight_rows.append([
            "Best Improvement",
            f"{format_concern_name(best['concern'])}"
            f"{format_percent(best.get('percent_change'))}"
        ])


    if highlights.get(
        "largest_decline"
    ):

        decline = highlights[
            "largest_decline"
        ]

        insight_rows.append([
            "Needs Attention",
            f"{format_concern_name(decline['concern'])}"
            f"{format_percent(decline.get('percent_change'))}"
        ])


    total_scans = consistency.get("total_scans")

    if total_scans is not None:

        insight_rows.append([
            "Scan Consistency",
            f"{total_scans} scans"
        ])


    if insight_rows:

        insight_table = Table(
            insight_rows,
            colWidths=[
                55 * mm,
                110 * mm
            ]
        )

        insight_table.setStyle(
            TableStyle([

                (
                    "BACKGROUND",
                    (0, 0),
                    (0, -1),
                    colors.HexColor("#f0f7f5")
                ),

                (
                    "FONTNAME",
                    (0, 0),
                    (0, -1),
                    "Helvetica-Bold"
                ),

                (
                    "VALIGN",
                    (0, 0),
                    (-1, -1),
                    "TOP"
                ),

                (
                    "GRID",
                    (0, 0),
                    (-1, -1),
                    0.5,
                    colors.HexColor("#e2e8f0")
                ),

                (
                    "TOPPADDING",
                    (0, 0),
                    (-1, -1),
                    9
                ),

                (
                    "BOTTOMPADDING",
                    (0, 0),
                    (-1, -1),
                    9
                ),

            ])
        )

        story.append(
            insight_table
        )

    else:

        add_no_data_note(
            story,
            normal_style,
            "Your personalized insights will appear here after your next scan."
        )


    # ==================================================
    # CONCERN STATUS
    # ==================================================

    concern_insights = insights.get(
        "concerns",
        {}
    )

    has_concern_status = any(
        concern_insights.get(category)
        for category in ("improved", "worsened", "stable")
    )

    if has_concern_status:

        story.append(
            Spacer(1, 15)
        )

        story.append(
            Paragraph(
                "Concern Status",
                styles["Heading3"]
            )
        )

        for category, concerns_list in concern_insights.items():

            if not concerns_list:
                continue

            story.append(
                Paragraph(
                    f"<b>{category.title()}</b>: "
                    + ", ".join(
                        format_concern_name(c)
                        for c in concerns_list
                    ),
                    normal_style
                )
            )

            story.append(
                Spacer(1, 5)
            )


    # ==================================================
    # LATEST CHANGES
    # ==================================================

    story.append(
        Spacer(1, 18)
    )

    story.append(
        Paragraph(
            "Latest Changes",
            heading_style
        )
    )

    trend_rows = [
        [
            "Metric",
            "Previous",
            "Current",
            "Change",
            "Direction"
        ]
    ]


    for metric_name, trend in [
        (
            "Overall Score",
            trends.get(
                "overall_score"
            )
        ),
        (
            "Skin Age",
            trends.get(
                "skin_age"
            )
        ),
    ]:

        if not trend:
            continue

        trend_rows.append([

            metric_name,

            format_value(trend.get("previous")),

            format_value(trend.get("current")),

            format_value(trend.get("change")),

            format_value(trend.get("direction")).title(),

        ])


    if len(trend_rows) > 1:

        trend_table = Table(
            trend_rows,
            colWidths=[
                40 * mm,
                30 * mm,
                30 * mm,
                30 * mm,
                35 * mm,
            ]
        )

        trend_table.setStyle(
            TableStyle([

                (
                    "BACKGROUND",
                    (0, 0),
                    (-1, 0),
                    colors.HexColor("#4a7c73")
                ),

                (
                    "TEXTCOLOR",
                    (0, 0),
                    (-1, 0),
                    colors.white
                ),

                (
                    "FONTNAME",
                    (0, 0),
                    (-1, 0),
                    "Helvetica-Bold"
                ),

                (
                    "ALIGN",
                    (1, 0),
                    (-1, -1),
                    "CENTER"
                ),

                (
                    "GRID",
                    (0, 0),
                    (-1, -1),
                    0.5,
                    colors.HexColor("#e2e8f0")
                ),

                (
                    "TOPPADDING",
                    (0, 0),
                    (-1, -1),
                    8
                ),

                (
                    "BOTTOMPADDING",
                    (0, 0),
                    (-1, -1),
                    8
                ),

            ])
        )

        story.append(
            trend_table
        )

    else:

        add_no_data_note(
            story,
            normal_style,
            "No changes to show yet — come back after your next scan to see what's changed."
        )


    # ==================================================
    # DISCLAIMER
    # ==================================================

    story.append(
        Spacer(1, 25)
    )

    story.append(
        Paragraph(
            "<b>Disclaimer:</b> "
            "This report is intended for informational "
            "and personal tracking purposes only. "
            "LuminaSkin's analysis does not constitute "
            "medical advice, diagnosis, or treatment.",
            ParagraphStyle(
                "Disclaimer",
                parent=normal_style,
                fontSize=8,
                textColor=colors.grey,
            )
        )
    )


    # ==================================================
    # FOOTER (page numbers + generated timestamp)
    # ==================================================

    def draw_footer(canvas, doc_):
        from datetime import datetime

        canvas.saveState()
        canvas.setFont("Helvetica", 8)
        canvas.setFillColor(colors.grey)

        canvas.drawString(
            18 * mm,
            12 * mm,
            f"Generated by LuminaSkin on {datetime.now().strftime('%d %b %Y, %I:%M %p')}"
        )

        canvas.drawRightString(
            A4[0] - 18 * mm,
            12 * mm,
            f"Page {doc_.page}"
        )

        canvas.restoreState()


    # ==================================================
    # BUILD
    # ==================================================

    doc.build(
        story,
        onFirstPage=draw_footer,
        onLaterPages=draw_footer,
    )



    for chart_path in chart_files:

        try:
            os.remove(chart_path)
        except OSError:
            pass

    buffer.seek(0)

    return buffer.getvalue()