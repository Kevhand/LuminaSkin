from skin.models.profile import CurrentRoutine, Product, SkinProfile, Lifestyle
from django.db import transaction

from django.shortcuts import get_object_or_404


from .module_selector import ModuleSelector
from . import build_ai_context
from . import analytics
from . select_context import ContextSelector
from dotenv import load_dotenv
from . import prompt_builder
from skin.views import build_chat_history, skin_profile
from . import routine_updater
from google.genai import types

load_dotenv()  # Load environment variables from .env file
from google import genai
import os

MODEL_NAMES = [
    "gemini-3.5-flash",
    "gemini-3.5-flash-lite",
] # Updated model name

class GeminiReasoner:
    def __init__(self):
        self.client = genai.Client(
            api_key=os.getenv("GOOGLE_API_KEY")
        )

    def generate(self, prompt):
        last_error = None

        for model_name in MODEL_NAMES:
            try:
                response = self.client.models.generate_content(
                    model=model_name,
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        tools=[
                            types.Tool(
                                google_search=types.GoogleSearch()
                            )
                        ],
                    )
                )

                return response.text

            except Exception as e:
                last_error = e
                print(f"{model_name} failed: {e}")

        raise last_error




class ChatEngine:

    def is_confirmation(self, message):
        confirmation_keywords = [
            "yes",
            "yeah",
            "yep",
            "yes please",
            "sure",
            "confirm",
            "confirmed",
            "do it",
            "update it",
            "go ahead",
            "okay",
            "ok",
            "alright",
            "sounds good",
        ]

        return message.strip().lower() in confirmation_keywords


    def is_rejection(self, message):
        rejection_keywords = [
            "no",
            "nope",
            "cancel",
            "don't",
            "dont",
            "don't update",
            "do not update",
            "stop",
            "not now",
            "not yet",
            "later",
            "maybe later",
            "break",
        ]

        return message.strip().lower() in rejection_keywords


    def cancel_routine_update(self, session):

        pending = session.metadata.get("pending_action")

        if pending and pending.get("type") == "routine_update":

            session.metadata.pop("pending_action", None)

            session.save(
                update_fields=["metadata", "updated_at"]
            )

            return {
                "response": "Routine update has been canceled.",
                "plan": {
                    "action": "chat"
                },
                "selected_context": {}
            }

        return {
            "response": "There is no routine update to cancel.",
            "plan": {
                "action": "chat"
            },
            "selected_context": {}
        }

    def cancel_profile_update(self, session):
        pending = session.metadata.get(
            "pending_action"
        )

        if pending and pending.get(
            "type"
        ) == "profile_update":

            session.metadata.pop(
                "pending_action",
                None
            )

            session.save(
                update_fields=[
                    "metadata",
                    "updated_at"
                ]
            )

            return {
                "response": "Profile update has been canceled.",
                "plan": {
                    "action": "chat"
                },
                "selected_context": {}
            }

        return {
            "response": (
                "There is no profile update to cancel."
            ),
            "plan": {
                "action": "chat"
            },
            "selected_context": {}
        }

    def cancel_lifestyle_update(self, session):
        pending = session.metadata.get("pending_action")

        if pending and pending.get("type") == "lifestyle_update":

            session.metadata.pop(
                "pending_action",
                None
            )

            session.save(
                update_fields=[
                    "metadata",
                    "updated_at"
                ]
            )

            return {
                "response": "Lifestyle update has been canceled.",
                "plan": {
                    "action": "chat"
                },
                "selected_context": {}
            }

        return {
            "response": "There is no lifestyle update to cancel.",
            "plan": {
                "action": "chat"
            },
            "selected_context": {}
        }


    def cancel_product_update(self, session):

        pending = session.metadata.get("pending_action")

        if pending and pending.get("type") in [
            "product_update",
            "product_add"
        ]:

            session.metadata.pop("pending_action", None)

            session.save(
                update_fields=["metadata", "updated_at"]
            )

            return {
                "response": "Product update has been canceled.",
                "plan": {
                    "action": "chat"
                },
                "selected_context": {}
            }

        return {
            "response": "There is no product update to cancel.",
            "plan": {
                "action": "chat"
            },
            "selected_context": {}
        }


    def chat(self, session, message, mode="chat"):

        # ---------------------------------
        # ROUTINE UPDATE MODE
        # ---------------------------------

        if mode == "routine_update":

            pending = session.metadata.get("pending_action")

            if pending and pending.get("type") == "routine_update":

                if self.is_confirmation(message):
                    return self.confirm_routine_update(session)

                if self.is_rejection(message):
                    return self.cancel_routine_update(session)

            return self.routine_update(
                session,
                message
            )

        # ---------------------------------
        # PROFILE UPDATE MODE
        # ---------------------------------

        if mode == "profile_update":

            pending = session.metadata.get(
                "pending_action"
            )

            if pending and pending.get(
                "type"
            ) == "profile_update":

                if self.is_confirmation(message):
                    return self.confirm_profile_update(
                        session
                    )

                if self.is_rejection(message):
                    return self.cancel_profile_update(
                        session
                    )

            return self.profile_update(
                session,
                message
            )
                

        # ---------------------------------
        # LIFESTYLE UPDATE MODE
        # ---------------------------------

        if mode == "lifestyle_update":
            pending = session.metadata.get("pending_action")

            if pending and pending.get("type") == "lifestyle_update":

                if self.is_confirmation(message):
                    return self.confirm_lifestyle_update(session)

                if self.is_rejection(message):
                    return self.cancel_lifestyle_update(session)

            skin_profile = SkinProfile.objects.get(
                user=session.user
            )

            return self.lifestyle_update(
                skin_profile,
                session,
                message
            )


        # ---------------------------------
        # PRODUCT UPDATE MODE
        # ---------------------------------

        if mode == "product_update":

            pending = session.metadata.get("pending_action")

            if pending and pending.get("type") in [
                "product_update",
                "product_add"
            ]:

                if self.is_confirmation(message):
                    skin_profile = SkinProfile.objects.get(
                        user=session.user
                    )

                    return self.confirm_product_update(
                        skin_profile,
                        session
                    )

                if self.is_rejection(message):
                    return self.cancel_product_update(session)

            skin_profile = SkinProfile.objects.get(
                user=session.user
            )

            return self.product_update(
                skin_profile,
                session,
                message
            )


        # ---------------------------------
        # NORMAL CHAT
        # ---------------------------------

        plan = ModuleSelector().create_plan(message)

        master_context = build_ai_context.generate_context(
            session.user
        )

        analytics_data = analytics.generate_user_analytics(
            session.user
        )

        selected_context = ContextSelector().select_context(
            master_context,
            analytics_data,
            plan
        )

        history = build_chat_history(session)

        history_text = ""

        if history:

            for msg in history:

                history_text += (
                    f"{msg['role'].capitalize()}: "
                    f"{msg['content']}\n"
                )

        prompt = prompt_builder.PromptBuilder().build_prompt(
            selected_context,
            message,
            history_text
        )

        try:

            response = GeminiReasoner().generate(prompt)

        except Exception as e:

            print(
                f"Error occurred while generating response: {e}"
            )

            response = (
                "Sorry, I encountered an error while "
                "processing the message."
            )

        return {
            "response": response,
            "plan": (
                plan.model_dump()
                if hasattr(plan, "model_dump")
                else str(plan)
            ),
            "selected_context": selected_context
        }
    # =============================
    # Profile Update
    # =============================

    def profile_update(self, session, message):
        profile = SkinProfile.objects.get(
        user=session.user
    )

        result = routine_updater.ProfileUpdater().extract(
            profile,
            message
        )

        proposed_profile = {
            "gender": result.gender,
            "age": result.age,
            "country": result.country,
            "skin_goals": result.skin_goals,
            "budget": result.budget,
            "allergies": result.allergies,
            "pregnancy_status": result.pregnancy_status,
            "vegan_cruelty_free": result.vegan_cruelty_free,
        }

        session.metadata["pending_action"] = {
            "type": "profile_update",
            "proposed_profile": proposed_profile
        }

        session.save(
            update_fields=["metadata", "updated_at"]
        )

        response = (
            "Here's what I understood "
            "about your profile update:\n\n"
        )

        response += f"Gender: {result.gender}\n"
        response += f"Age: {result.age}\n"
        response += f"Country: {result.country}\n"

        response += (
            f"Skin Goals: "
            f"{', '.join(result.skin_goals or [])}\n"
        )

        response += f"Budget: {result.budget}\n"

        response += (
            f"Allergies: "
            f"{', '.join(result.allergies or [])}\n"
        )

        response += (
            f"Pregnancy Status: "
            f"{result.pregnancy_status}\n"
        )

        response += (
            f"Vegan / Cruelty Free: "
            f"{result.vegan_cruelty_free}\n"
        )

        response += (
            "\n\nWould you like me to update "
            "your profile with these changes?"
        )

        return {
            "response": response,
            "plan": {
                "action": "profile_update"
            },
            "selected_context": {
                "proposed_profile": proposed_profile
            }
        }

    

    # =============================
    # Lifestyle Update
    # =============================

    def lifestyle_update(self, skin_profile, session, message):
        lifestyle = Lifestyle.objects.get(profile=skin_profile)

        result = routine_updater.LifestyleUpdater().extract(
            lifestyle,
            message
        )

        proposed_lifestyle = {
            "sleep_hours": result.sleep_hours,
            "water_intake": result.water_intake,
            "stress_level": result.stress_level,
            "smoking": result.smoking,
            "alcohol_consumption": result.alcohol_consumption,
            "exercise_frequency": result.exercise_frequency,
            "exercise_hours_per_week": result.exercise_hours_per_week,
            "sun_exposure": result.sun_exposure,
            "spf_usage": result.spf_usage,
        }

        session.metadata["pending_action"] = {
            "type": "lifestyle_update",
            "proposed_lifestyle": proposed_lifestyle
        }

        session.save(
            update_fields=["metadata", "updated_at"]
        )

        response = "Here's what I understood about your lifestyle update:\n\n"

        response += f"Sleep Hours: {result.sleep_hours}\n"
        response += f"Water Intake: {result.water_intake}\n"
        response += f"Stress Level: {result.stress_level}\n"
        response += f"Smoking: {result.smoking}\n"
        response += f"Alcohol Consumption: {result.alcohol_consumption}\n"
        response += f"Exercise Frequency: {result.exercise_frequency}\n"
        response += f"Exercise Hours Per Week: {result.exercise_hours_per_week}\n"
        response += f"Sun Exposure: {result.sun_exposure}\n"
        response += f"SPF Usage: {result.spf_usage}\n"

        response += (
            "\n\nWould you like me to update "
            "your lifestyle information with these changes?"
        )

        return {
            "response": response,
            "plan": {
                "action": "lifestyle_update"
            },
            "selected_context": {
                "proposed_lifestyle": proposed_lifestyle
            }
        }

    # =================================
    # ROUTINE UPDATE
    # =================================

    def routine_update(self, session, message):

        routine = CurrentRoutine.objects.get(
            profile__user=session.user
        )

        result = routine_updater.RoutineUpdater().extract(
            routine,
            message
        )

        proposed_routine = {
            "morning_routine": result.morning_routine,
            "night_routine": result.night_routine,
        }

        session.metadata["pending_action"] = {
            "type": "routine_update",
            "proposed_routine": proposed_routine
        }

        session.save(
            update_fields=["metadata", "updated_at"]
        )

        morning = result.morning_routine or []
        night = result.night_routine or []

        response = "Here's what I understood:\n\n"

        response += "Morning Routine:\n"

        if morning:

            response += (
                "\n".join(
                    f"• {item}"
                    for item in morning
                )
                + "\n"
            )

        else:

            response += "• No changes\n"

        response += "\n"

        response += "Night Routine:\n"

        if night:

            response += (
                "\n".join(
                    f"• {item}"
                    for item in night
                )
                + "\n"
            )

        else:

            response += "• No changes\n"

        response += (
            "\n\nWould you like me to update "
            "your routine with these changes?"
        )

        return {
            "response": response,
            "plan": {
                "action": "routine_update"
            },
            "selected_context": {
                "proposed_routine": proposed_routine
            }
        }


    # =================================
    # PRODUCT UPDATE / ADD
    # =================================

    def product_update(
        self,
        skin_profile,
        session,
        message
    ):

        products = Product.objects.filter(
            profile=skin_profile
        )

        result = routine_updater.ProductUpdater().extract(
            products,
            message
        )

        print("AI PRODUCT RESULT:")
        print("Brand:", result.brand)
        print("Name:", result.product_name)
        print("Type:", result.product_type)


        # ---------------------------------
        # Try to find existing product
        # ---------------------------------

        product = None

        if result.brand and result.product_name:

            product = products.filter(
                brand__iexact=result.brand,
                product_name__iexact=result.product_name
            ).first()


        if not product and result.product_name:

            product = products.filter(
                product_name__iexact=result.product_name
            ).first()


        if not product and result.brand and result.product_type:

            product = products.filter(
                brand__iexact=result.brand,
                product_type__iexact=result.product_type
            ).first()


        # ---------------------------------
        # Determine whether this is an
        # update or a new product
        # ---------------------------------

        if product:

            action_type = "product_update"
            product_pk = product.pk

            confirmation_text = (
                "Would you like me to update "
                "your product information with "
                "these changes?"
            )

        else:

            action_type = "product_add"
            product_pk = None

            confirmation_text = (
                "I couldn't find this product in "
                "your current products. Would you "
                "like me to add it to your products?"
            )


        # ---------------------------------
        # Values for confirmation display
        # ---------------------------------

        effectiveness_rating = (
            result.effectiveness_rating
            if result.effectiveness_rating is not None
            else "No changes"
        )

        is_current = (
            result.is_current
            if result.is_current is not None
            else "No changes"
        )


        # ---------------------------------
        # Proposed product
        # ---------------------------------

        proposed_products = {

            "product_name": result.product_name,

            "brand": result.brand,

            "product_type": result.product_type,

            "ingredients": result.ingredients,

            "effectiveness_rating":
                result.effectiveness_rating,

            "side_effects":
                result.side_effects,

            "is_current":
                result.is_current,

            "usage_frequency":
                result.usage_frequency,
        }


        # ---------------------------------
        # Store pending action
        # ---------------------------------

        session.metadata["pending_action"] = {

            "type": action_type,

            # Only used internally when updating
            # an existing product.
            "product_pk": product_pk,

            "proposed_products": proposed_products
        }

        session.save(
            update_fields=["metadata", "updated_at"]
        )


        # ---------------------------------
        # Build confirmation message
        # ---------------------------------

        product_name = (
            result.product_name or ""
        )

        brand = (
            result.brand or ""
        )

        product_type = (
            result.product_type or ""
        )

        ingredients = (
            result.ingredients or []
        )

        side_effects = (
            result.side_effects or []
        )

        usage_frequency = (
            result.usage_frequency
            if result.usage_frequency is not None
            else "No changes"
        )


        response = (
            "Here's what I understood "
            "about the product:\n\n"
        )

        response += (
            f"Product Name: {product_name}\n"
        )

        response += (
            f"Brand: {brand}\n"
        )

        response += (
            f"Type: {product_type}\n"
        )

        response += (
            f"Ingredients: "
            f"{', '.join(ingredients)}\n"
        )

        response += (
            f"Effectiveness Rating: "
            f"{effectiveness_rating}\n"
        )

        response += (
            f"Side Effects: "
            f"{', '.join(side_effects)}\n"
        )

        response += (
            f"Is Current: {is_current}\n"
        )

        response += (
            f"Usage Frequency: "
            f"{usage_frequency}\n"
        )

        response += (
            f"\n\n{confirmation_text}"
        )


        return {
            "response": response,
            "plan": {
                "action": action_type
            },
            "selected_context": {
                "proposed_products":
                    proposed_products
            }
        }

    # =============================
    # CONFIRM PROFILE UPDATE
    # ============================

    def confirm_profile_update(self, session):
        pending_action = session.metadata.get(
            "pending_action"
        )

        if not pending_action:

            return {
                "response": (
                    "There is no profile update "
                    "pending confirmation."
                ),
                "plan": {
                    "action": "chat"
                },
                "selected_context": {}
            }

        if pending_action.get("type") != "profile_update":

            return {
                "response": (
                    "There is no profile update "
                    "waiting for confirmation."
                ),
                "plan": {
                    "action": "chat"
                },
                "selected_context": {}
            }

        proposed_profile = pending_action.get(
            "proposed_profile",
            {}
        )

        profile = SkinProfile.objects.get(
            user=session.user
        )

        with transaction.atomic():

            profile.gender = proposed_profile.get(
                "gender",
                profile.gender
            )

            profile.age = proposed_profile.get(
                "age",
                profile.age
            )

            profile.country = proposed_profile.get(
                "country",
                profile.country
            )

            profile.skin_goals = proposed_profile.get(
                "skin_goals",
                profile.skin_goals
            )

            profile.budget = proposed_profile.get(
                "budget",
                profile.budget
            )

            profile.allergies = proposed_profile.get(
                "allergies",
                profile.allergies
            )

            profile.pregnancy_status = proposed_profile.get(
                "pregnancy_status",
                profile.pregnancy_status
            )

            profile.vegan_cruelty_free = proposed_profile.get(
                "vegan_cruelty_free",
                profile.vegan_cruelty_free
            )

            profile.save()

            session.metadata.pop(
                "pending_action",
                None
            )

            session.save(
                update_fields=[
                    "metadata",
                    "updated_at"
                ]
            )

        return {
            "response": (
                "Your profile information has "
                "been successfully updated."
            ),
            "mode": "chat",
            "plan": {
                "action": "profile_update_confirmed"
            },
            "selected_context": {
                "updated_profile": {
                    "gender": profile.gender,
                    "age": profile.age,
                    "country": profile.country,
                    "skin_goals": profile.skin_goals,
                    "budget": profile.budget,
                    "allergies": profile.allergies,
                    "pregnancy_status":
                        profile.pregnancy_status,
                    "vegan_cruelty_free":
                        profile.vegan_cruelty_free
                }
            }
        }



    # =================================
    # CONFIRM ROUTINE UPDATE
    # =================================

    def confirm_routine_update(self, session):

        pending_action = session.metadata.get(
            "pending_action"
        )

        if not pending_action:

            return {
                "response": (
                    "There is no routine update "
                    "pending confirmation."
                ),
                "plan": {
                    "action": "chat"
                },
                "selected_context": {}
            }


        if pending_action.get(
            "type"
        ) != "routine_update":

            return {
                "response": (
                    "There is no routine update "
                    "waiting for confirmation."
                ),
                "plan": {
                    "action": "chat"
                },
                "selected_context": {}
            }


        proposed_routine = pending_action.get(
            "proposed_routine",
            {}
        )

        routine = CurrentRoutine.objects.get(
            profile__user=session.user
        )


        with transaction.atomic():

            routine.morning_routine = (
                proposed_routine.get(
                    "morning_routine",
                    routine.morning_routine
                )
            )

            routine.night_routine = (
                proposed_routine.get(
                    "night_routine",
                    routine.night_routine
                )
            )

            routine.save(
                update_fields=[
                    "morning_routine",
                    "night_routine"
                ]
            )

            session.metadata.pop(
                "pending_action",
                None
            )

            session.save(
                update_fields=[
                    "metadata",
                    "updated_at"
                ]
            )


        return {
            "response": (
                "Your skincare routine has "
                "been successfully updated."
            ),
            "mode": "chat",
            "plan": {
                "action": "routine_update_confirmed"
            },
            "selected_context": {
                "updated_routine": {
                    "morning_routine":
                        routine.morning_routine,

                    "night_routine":
                        routine.night_routine
                }
            }
        }

    # =================================
    # Confirm Lifestyle Update
    # =================================

    def confirm_lifestyle_update(self, session):
        pending_action = session.metadata.get("pending_action")

        if not pending_action:
            return {
                "response": (
                    "There is no lifestyle update "
                    "pending confirmation."
                ),
                "plan": {
                    "action": "chat"
                },
                "selected_context": {}
            }

        if pending_action.get("type") != "lifestyle_update":

            return {
                "response": (
                    "There is no lifestyle update "
                    "waiting for confirmation."
                ),
                "plan": {
                    "action": "chat"
                },
                "selected_context": {}
            }

        proposed_lifestyle = pending_action.get(
            "proposed_lifestyle",
            {}
        )

        lifestyle = Lifestyle.objects.get(
            profile__user=session.user
        )

        with transaction.atomic():

            lifestyle.sleep_hours = proposed_lifestyle.get(
                "sleep_hours",
                lifestyle.sleep_hours
            )

            lifestyle.water_intake = proposed_lifestyle.get(
                "water_intake",
                lifestyle.water_intake
            )

            lifestyle.stress_level = proposed_lifestyle.get(
                "stress_level",
                lifestyle.stress_level
            )

            lifestyle.smoking = proposed_lifestyle.get(
                "smoking",
                lifestyle.smoking
            )

            lifestyle.alcohol_consumption = proposed_lifestyle.get(
                "alcohol_consumption",
                lifestyle.alcohol_consumption
            )

            lifestyle.exercise_frequency = proposed_lifestyle.get(
                "exercise_frequency",
                lifestyle.exercise_frequency
            )

            lifestyle.exercise_hours_per_week = proposed_lifestyle.get(
                "exercise_hours_per_week",
                lifestyle.exercise_hours_per_week
            )

            lifestyle.sun_exposure = proposed_lifestyle.get(
                "sun_exposure",
                lifestyle.sun_exposure
            )

            lifestyle.spf_usage = proposed_lifestyle.get(
                "spf_usage",
                lifestyle.spf_usage
            )

            lifestyle.save()

            session.metadata.pop(
                "pending_action",
                None
            )

            session.save(
                update_fields=[
                    "metadata",
                    "updated_at"
                ]
            )

        return {
            "response": (
                "Your lifestyle information has "
                "been successfully updated."
            ),
            "mode": "chat",
            "plan": {
                "action": "lifestyle_update_confirmed"
            },
            "selected_context": {
                "updated_lifestyle": {
                    "sleep_hours": lifestyle.sleep_hours,
                    "water_intake": lifestyle.water_intake,
                    "stress_level": lifestyle.stress_level,
                    "smoking": lifestyle.smoking,
                    "alcohol_consumption": lifestyle.alcohol_consumption,
                    "exercise_frequency": lifestyle.exercise_frequency,
                    "exercise_hours_per_week":
                        lifestyle.exercise_hours_per_week,
                    "sun_exposure": lifestyle.sun_exposure,
                    "spf_usage": lifestyle.spf_usage
                }
            }
        }



    # =================================
    # CONFIRM PRODUCT UPDATE / ADD
    # =================================

    def confirm_product_update(self, skin_profile, session):

        pending_action = session.metadata.get(
            "pending_action"
        )


        if not pending_action:

            return {
                "response": (
                    "There is no product action "
                    "pending confirmation."
                ),
                "plan": {
                    "action": "chat"
                },
                "selected_context": {}
            }


        pending_type = pending_action.get(
            "type"
        )


        if pending_type not in [
            "product_update",
            "product_add"
        ]:

            return {
                "response": (
                    "There is no product action "
                    "waiting for confirmation."
                ),
                "plan": {
                    "action": "chat"
                },
                "selected_context": {}
            }


        proposed_products = pending_action.get(
            "proposed_products",
            {}
        )


        # ---------------------------------
        # ADD NEW PRODUCT
        # ---------------------------------

        if pending_type == "product_add":

            with transaction.atomic():

                product = Product.objects.create(
                    profile=skin_profile,
                    brand=proposed_products.get("brand"),
                    product_name=proposed_products.get("product_name"),
                    product_type=proposed_products.get("product_type"),
                    ingredients=proposed_products.get("ingredients") or [],
                    effectiveness_rating=proposed_products.get("effectiveness_rating"),
                    side_effects=proposed_products.get("side_effects") or [],
                    is_current=(
                        proposed_products.get("is_current")
                        if proposed_products.get("is_current") is not None
                        else True
                    ),
                    usage_frequency=proposed_products.get("usage_frequency")
                )


                session.metadata.pop(
                    "pending_action",
                    None
                )

                session.save(
                    update_fields=[
                        "metadata",
                        "updated_at"
                    ]
                )


            return {
                "response": (
                    "Your skincare product has "
                    "been successfully added."
                ),
                "mode": "chat",
                "plan": {
                    "action": "product_added"
                },
                "selected_context": {
                    "added_product": {

                        "product_name":
                            product.product_name,

                        "brand":
                            product.brand,

                        "product_type":
                            product.product_type,

                        "ingredients":
                            product.ingredients,

                        "effectiveness_rating":
                            product.effectiveness_rating,

                        "side_effects":
                            product.side_effects,

                        "is_current":
                            product.is_current,

                        "usage_frequency":
                            product.usage_frequency
                    }
                }
            }


        # ---------------------------------
        # UPDATE EXISTING PRODUCT
        # ---------------------------------

        product_pk = pending_action.get(
            "product_pk"
        )


        if not product_pk:

            return {
                "response": (
                    "I couldn't identify the "
                    "product to update."
                ),
                "plan": {
                    "action": "chat"
                },
                "selected_context": {}
            }


        product = get_object_or_404(
            Product,
            pk=product_pk,
            profile__user=session.user
        )


        with transaction.atomic():

            product.product_name = (
                proposed_products.get(
                    "product_name",
                    product.product_name
                )
            )

            product.brand = (
                proposed_products.get(
                    "brand",
                    product.brand
                )
            )

            product.product_type = (
                proposed_products.get(
                    "product_type",
                    product.product_type
                )
            )

            product.ingredients = (
                proposed_products.get(
                    "ingredients",
                    product.ingredients
                )
            )

            product.effectiveness_rating = (
                proposed_products.get(
                    "effectiveness_rating",
                    product.effectiveness_rating
                )
            )

            product.side_effects = (
                proposed_products.get(
                    "side_effects",
                    product.side_effects
                )
            )

            product.is_current = (
                proposed_products.get(
                    "is_current",
                    product.is_current
                )
            )

            product.usage_frequency = (
                proposed_products.get(
                    "usage_frequency",
                    product.usage_frequency
                )
            )


            product.save()


            session.metadata.pop(
                "pending_action",
                None
            )

            session.save(
                update_fields=[
                    "metadata",
                    "updated_at"
                ]
            )


        return {
            "response": (
                "Your skincare product information "
                "has been successfully updated."
            ),
            "mode": "chat",
            "plan": {
                "action": "product_update_confirmed"
            },
            "selected_context": {
                "updated_product": {

                    "product_name":
                        product.product_name,

                    "brand":
                        product.brand,

                    "product_type":
                        product.product_type,

                    "ingredients":
                        product.ingredients,

                    "effectiveness_rating":
                        product.effectiveness_rating,

                    "side_effects":
                        product.side_effects,

                    "is_current":
                        product.is_current,

                    "usage_frequency":
                        product.usage_frequency
                }
            }
        }