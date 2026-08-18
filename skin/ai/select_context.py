
class ContextSelector:
    def select_context(self, master_context, analytics_data, plan):
        mapping = {

            "profile": master_context["profile"]["skin_profile"],

            "lifestyle": master_context["profile"]["lifestyle"],

            "routine": master_context["profile"]["current_routine"],

            "products": master_context["profile"]["products"],

            "latest_scan": master_context["current_state"]["latest_scan"],

            "trends": master_context["trends"],

            "analytics_summary": analytics_data["summary"],

            "insights": analytics_data["insights"],

        }

        selected_context = {}

        for module in plan.modules:
            if module in mapping:
                selected_context[module] = mapping[module]
        return {
            "action": plan.action,
            "confidence": plan.confidence,
            "context": selected_context
        }




