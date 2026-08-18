
from django.utils import timezone

from skin.models.scan import Scan, ScanResult

from . import trend_engine


def build_overall_scan_history(user):
    """
    Build a history of overall scan scores for the user.
    """
    scans = Scan.objects.filter(user=user).order_by('date_created')
    history = []

    for scan in scans:
        history.append({
            "scan_id": scan.scan_id,
            "overall_score": scan.overall_score,
            "date": scan.date_created.isoformat(),
        })

    return history


def skin_age_history(user):
    """
    Build a history of skin age for the user.
    """
    scans = Scan.objects.filter(user=user).order_by('date_created')
    history = []

    for scan in scans:
        history.append({
            "scan_id": scan.scan_id,
            "skin_age": scan.skin_age,
            "date": scan.date_created.isoformat(),
        })

    return history


def concern_history(user, concern):
    """
    Build a history of scores for a specific skin concern for the user.
    """
    scans = Scan.objects.filter(user=user).order_by('date_created')

    results = ScanResult.objects.filter(scan__user=user, skin_concern=concern).select_related("scan").order_by("scan__date_created")

    history = []

    for result in results:
        history.append({
            "scan_id": result.scan.scan_id,
            "ui_score": result.ui_score,
            "raw_score": result.raw_score,
            "date": result.scan.date_created.isoformat(),
        })


    return history



def build_line_graph(history, score_key):
    return {
        "labels":[
            item["date"] for item in history
        ],
        "values": [
            item[score_key] for item in history
        ]
    }


def build_graph_data(user):
    """
    Build graph data for overall scan scores, skin age, and specific skin concerns.
    """
    overall_scan_history = build_overall_scan_history(user)
    skin_age_history_data = skin_age_history(user)

    # Get all unique concerns from the user's scans
    unique_concerns = ScanResult.objects.filter(scan__user=user).values_list('skin_concern', flat=True).distinct()


    graphs = {
        "overall_score": build_line_graph(overall_scan_history, "overall_score"),
        "skin_age": build_line_graph(skin_age_history_data, "skin_age"),
        "concerns": {}
    }



    for concern in unique_concerns:
        history = concern_history(user, concern)

        graphs["concerns"][concern] = {
            "ui_score": build_line_graph(history, "ui_score"),
        }


    return graphs


def generate_summary(user):
    """
    Generate a summary of the user's Scan history
    """

    scans = Scan.objects.filter(user=user).order_by('date_created')

    if not scans.exists():
        return {}

    latest_scan = scans.last()
    first_scan = scans.first()

    concerns = ScanResult.objects.filter(scan__user=user).values_list('skin_concern', flat=True).distinct()


    summary = {
        "total_scans": scans.count(),
        "first_scan_date": first_scan.date_created.isoformat(),
        "latest_scan_date": latest_scan.date_created.isoformat(),
        "days_since_last_scan": (timezone.now() - latest_scan.date_created).days,
        "latest_overall_score": round(latest_scan.overall_score, 2) if latest_scan.overall_score is not None else None,
        "latest_skin_age": latest_scan.skin_age,
        "latest_skin_type": latest_scan.skin_type,
        "latest_selected_concerns": latest_scan.selected_concern,
        "concerns_tracked": len(concerns),
    }

    return summary



def generate_insights(user):
    trends = trend_engine.calculate_trends(user)

    if not trends:
        return {
            "progress": {},
            "concerns": {},
            "consistency": {},
            "highlights": {},
        }
    scan = Scan.objects.filter(user=user).order_by('date_created')

    scan_count = scan.count()

    latest_scan = scan.last()

    insights = {
        "progress": {},
        "concerns": {},
        "consistency": {},
        "highlights": {}
    }

    insights["concerns"] = {
        "improved": [],
        "worsened": [],
        "stable": []
    }

    insights["progress"] = {
        "overall_direction": trends["overall_score"]["direction"] if trends else None,
        "overall_change": trends["overall_score"]["change"] if trends else None,

        "skin_age_direction": trends["skin_age"]["direction"] if trends else None,
        "skin_age_change": trends["skin_age"]["change"] if trends else None,
    }

    best_improvement = None
    best_change = 0


    largest_decline = None
    worse_decline = 0

    for concern, value in (trends.get("concerns") or {}).items():
        
        ui_score = value.get("ui_score")
        direction = ui_score.get("direction") if ui_score else None
        if direction == "improving":
            improvement = abs(value["ui_score"]["change"])

            if improvement > best_change:
                best_change = improvement
                best_improvement = {
                    "concern": concern,
                    "change": value["ui_score"]["change"],
                    "percent_change": value["ui_score"]["percent_change"]
                }
                
            insights["concerns"]["improved"].append(concern)

            

        elif direction == "worsening":
            insights["concerns"]["worsened"].append(concern)

            decline = abs(value["ui_score"]["change"])

            if decline > worse_decline:
                worse_decline = decline
                largest_decline = {
                    "concern": concern,
                    "change": value["ui_score"]["change"],
                    "percent_change": value["ui_score"]["percent_change"]
                }
        elif direction == "stable":
            insights["concerns"]["stable"].append(concern)

    insights["consistency"] = {
        "total_scans": scan_count,
        "days_since_last_scan": (timezone.now() - latest_scan.date_created).days if latest_scan else None,
    } 


    insights["highlights"] = {
        "best_improvement": best_improvement,
        "largest_decline": largest_decline,
    }

    return insights



def generate_user_analytics(user):
    """
    Generate a comprehensive analytics report for the user.
    """
    graphs = build_graph_data(user)
    summary = generate_summary(user)
    insights = generate_insights(user)

    return {
        "graphs": graphs,
        "summary": summary,
        "insights": insights
    }