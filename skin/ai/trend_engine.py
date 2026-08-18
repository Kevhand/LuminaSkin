from skin.models.scan import Scan, ScanResult


def compare_metric(current, previous, lower_is_better=False):

    if current is None:
        return {
            "current": None,
            "previous": previous,
            "change": None,
            "percent_change": None,
            "direction": "unavailable"
        }

    if previous is None:
        return {
            "current": round(current, 1),
            "previous": None,
            "change": None,
            "percent_change": None,
            "direction": "baseline"
        }

    # Calculate using full precision
    change_raw = current - previous

    percent_change_raw = (
        (change_raw / previous) * 100
        if previous != 0
        else None
    )

    # Determine direction using raw values
    if (
        change_raw == 0
        or abs(change_raw) < 0.5
        or (
            percent_change_raw is not None
            and abs(percent_change_raw) < 1
        )
    ):
        direction = "stable"

    elif lower_is_better:
        direction = (
            "improving"
            if change_raw < 0
            else "worsening"
        )

    else:
        direction = (
            "improving"
            if change_raw > 0
            else "worsening"
        )

    # Round only what gets returned
    return {
        "current": round(current, 1),
        "previous": round(previous, 1),
        "change": round(change_raw, 1),
        "percent_change": (
            round(percent_change_raw, 1)
            if percent_change_raw is not None
            else None
        ),
        "direction": direction
    }



def calculate_overall_score(latest_scan, previous_scan):
    """
    Calculate the overall score for the latest scan compared to the previous scan.
    """
    previous_score = (
        previous_scan.overall_score
        if previous_scan is not None
        else None
    )


    return compare_metric(
        current=latest_scan.overall_score,
        previous=previous_score,
        lower_is_better=False
    )


def calculate_skin_age(latest_scan, previous_scan):
    """
    Calculate the skin age for the latest scan compared to the previous scan.
    """
    previous_skin_age = (
        previous_scan.skin_age
        if previous_scan is not None
        else None
    )

    return compare_metric(
        current=latest_scan.skin_age,
        previous=previous_skin_age,
        lower_is_better=True
    )



def calculate_concern_trends(user, latest_scan):
    concern_trends = {}
    latest_results = ScanResult.objects.filter(scan=latest_scan)

    if not latest_results:
        return None
    for result in latest_results:
        previous_result = (
            ScanResult.objects.filter(
                scan__user = user,
                skin_concern = result.skin_concern,
                scan__date_created__lt = latest_scan.date_created
            ).order_by("-scan__date_created").first()
        )

        concern_trends[result.skin_concern] = {
            "ui_score": compare_metric(
                current = result.ui_score,
                previous = previous_result.ui_score if previous_result else None,
                lower_is_better = False
            ),
        }
    return concern_trends





def calculate_trends(user):
    latest_scan = Scan.objects.filter(user=user).order_by("-date_created").first()
    previous_scan = Scan.objects.filter(user=user).order_by("-date_created")[1:2].first()

    if not latest_scan:
        return None
    if not previous_scan:
        return {
            "overall_score": calculate_overall_score(latest_scan, None),
            "skin_age": calculate_skin_age(latest_scan, None)
        }

    trends = {
        "overall_score": calculate_overall_score(latest_scan, previous_scan),
        "skin_age": calculate_skin_age(latest_scan, previous_scan),
        "concerns": calculate_concern_trends(user, latest_scan)
    }

    return trends
