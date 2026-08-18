from . import analytics
from . import trend_engine


def generate_report_data(user):
    analytics_data = analytics.generate_user_analytics(user)


    return {
        "summary": analytics_data.get("summary", {}),
        "insights": analytics_data.get("insights", {}),
        "graphs": analytics_data.get("graphs", {}),
        "trends": trend_engine.calculate_trends(user)
    }


