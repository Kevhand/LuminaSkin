from django.utils import timezone
from skin.models import SkinProfile, Lifestyle, CurrentRoutine, Product, Scan, ScanResult
from . import trend_engine


def generate_context(user):
    """
    Builds a complete structured context for the AI.
    Returns a dictionary only.
    """

    context = {
        "metadata": {},
        "profile": {},
        "current_state": {},
        "trends": {},
        "missing_information": [],
    }

    skin_profile, _= SkinProfile.objects.get_or_create(user=user)
    lifestyle, _ = Lifestyle.objects.get_or_create(profile=skin_profile)
    current_routine, _ = CurrentRoutine.objects.get_or_create(profile=skin_profile)
    products = Product.objects.filter(profile=skin_profile)

    latest_scan = Scan.objects.filter(user=user).order_by('-date_created').first()

    scan_count = Scan.objects.filter(user=user).order_by('-date_updated').count()


    context["metadata"] = {
        "username": user.username,
        "email": user.email,
        "date_joined": user.date_joined.isoformat(),
        "scan_count": scan_count,
        "latest_scan_date": latest_scan.date_created.isoformat() if latest_scan else None,
        "version": "2.0",
    }


    context["profile"]["skin_profile"] = {
        "gender": skin_profile.gender,
        "age": skin_profile.age,
        "country": skin_profile.country,
        "skin_goals": skin_profile.skin_goals,
        "budget": skin_profile.budget,
        "allergies": skin_profile.allergies,
        "pregnancy_status": skin_profile.pregnancy_status,
        "vegan_cruelty_free": skin_profile.vegan_cruelty_free,
    }


    context["profile"]["lifestyle"] = {
        "sleep_hours": lifestyle.sleep_hours,
        "water_intake": lifestyle.water_intake,
        "stress_level": lifestyle.stress_level,
        "smoking": lifestyle.smoking,
        "alcohol_consumption": lifestyle.alcohol_consumption,
        "exercise_frequency": lifestyle.exercise_frequency,
        "exercise_hours_per_week": lifestyle.exercise_hours_per_week,
        "sun_exposure": lifestyle.sun_exposure,
        "spf_usage": lifestyle.spf_usage,
    }

    context["profile"]["current_routine"] = {
        "morning_routine": current_routine.morning_routine,
        "night_routine": current_routine.night_routine,
    }

    context["profile"]["products"] = [
        {   
            "product_name": product.product_name,
            "product_type": product.product_type,
            "brand": product.brand,
            "ingredients": product.ingredients,
            "usage_frequency": product.usage_frequency,
            "effectiveness_rating": product.effectiveness_rating,
            "side_effects": product.side_effects,
            "is_current": product.is_current,
        }
        for product in products
    ]

    context["current_state"]["latest_scan"] = {
        "scan_id": latest_scan.scan_id if latest_scan else None,
        "overall_score": latest_scan.overall_score if latest_scan else None,
        "skin_age": latest_scan.skin_age if latest_scan else None,
        "skin_type": latest_scan.skin_type if latest_scan else None,
        "selected_concern": latest_scan.selected_concern if latest_scan else None,
        "date_created": latest_scan.date_created.isoformat() if latest_scan else None,
        "date_updated": latest_scan.date_updated.isoformat() if latest_scan else None,
        "results": [
            {
                "skin_concern": result.skin_concern,
                "ui_score": result.ui_score,
                "raw_score": result.raw_score,
                "status": result.status,
            }
            for result in (latest_scan.results.all() if latest_scan else [])
        ]
    }

    context["trends"] = trend_engine.calculate_trends(user)

    context["current_state"]["summary"] = {
        "overall_score": latest_scan.overall_score if latest_scan else None,
        "skin_age": latest_scan.skin_age if latest_scan else None,
        "skin_type": latest_scan.skin_type if latest_scan else None,
        "conerns_scanned": len(latest_scan.results.all()) if latest_scan else 0,
        "selected_concerns": latest_scan.selected_concern if latest_scan else None,
    }


    context["missing_information"] = {
        "skin_profile": [],
        "lifestyle": [],
        "current_routine": [],
        "products": []
    }

    # Check for missing information in skin profile
    if not skin_profile.gender:
        context["missing_information"]["skin_profile"].append("gender")

    if not skin_profile.age:
        context["missing_information"]["skin_profile"].append("age")

    if not skin_profile.skin_goals:
        context["missing_information"]["skin_profile"].append("skin_goals")

    if not skin_profile.budget:
        context["missing_information"]["skin_profile"].append("budget")

    if not skin_profile.allergies:
        context["missing_information"]["skin_profile"].append("allergies")

    if not skin_profile.pregnancy_status:
        context["missing_information"]["skin_profile"].append("pregnancy_status")

    if not skin_profile.vegan_cruelty_free:
        context["missing_information"]["skin_profile"].append("vegan_cruelty_free")

    # Lifestyle checks
    if not lifestyle.sleep_hours:
        context["missing_information"]["lifestyle"].append("sleep_hours")

    if not lifestyle.water_intake:
        context["missing_information"]["lifestyle"].append("water_intake")

    if not lifestyle.stress_level:
        context["missing_information"]["lifestyle"].append("stress_level")

    if not lifestyle.smoking:
        context["missing_information"]["lifestyle"].append("smoking")

    if not lifestyle.alcohol_consumption:
        context["missing_information"]["lifestyle"].append("alcohol_consumption")

    if not lifestyle.exercise_frequency:
        context["missing_information"]["lifestyle"].append("exercise_frequency")

    if not lifestyle.exercise_hours_per_week:
        context["missing_information"]["lifestyle"].append("exercise_hours_per_week")

    if not lifestyle.sun_exposure:
        context["missing_information"]["lifestyle"].append("sun_exposure")

    if not lifestyle.spf_usage:
        context["missing_information"]["lifestyle"].append("spf_usage")


    # Current routine checks
    if not current_routine.morning_routine:
        context["missing_information"]["current_routine"].append("morning_routine")

    if not current_routine.night_routine:
        context["missing_information"]["current_routine"].append("night_routine")


    # Product checks
    if not products.exists():
        context["missing_information"]["products"].append("No products added")

    return context

