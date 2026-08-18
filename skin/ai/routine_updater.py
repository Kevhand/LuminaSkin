from django.template import response
from pydantic import BaseModel
from google import genai
from google.genai import types

import os


MODEL_NAMES = [
    "gemini-3.5-flash",
    "gemini-3.5-flash-lite",
]




class RoutineUpdate(BaseModel):
    morning_routine :list[str] | None 
    night_routine :list[str] | None


class RoutineUpdater:
    def __init__(self):
        self.client = genai.Client(api_key=os.getenv('GOOGLE_API_KEY')) 


    def extract(self, current_routine, user_message):
        prompt = f"""
            You are LuminaSkin's routine update assistant.

            The user wants to update their skincare routine.

            Current routine:

            Morning:
            {current_routine.morning_routine or []}

            Night:
            {current_routine.night_routine or []}

            The user said:

            {user_message}

            Your task is to understand what the user wants to change.

            Return the COMPLETE resulting morning and night routines.

            Rules:

            1. Only modify information that the user actually indicates.
            2. Preserve existing routine items when the user does not mention changing them.
            3. If the user explicitly removes a product, remove it.
            4. If the user explicitly adds a product, add it.
            5. If the user replaces one product with another, perform the replacement.
            6. Do not invent products or routine steps.
            7. Return routines as lists of strings.
            8. If a routine was not affected, return its existing routine unchanged.
        """
        last_error = None

        for model_name in MODEL_NAMES:
            try:
                response = self.client.models.generate_content(
                    model=model_name,
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        response_mime_type="application/json",
                        response_schema=RoutineUpdate,
                        temperature=0.2,
                    )
                )

                return response.parsed

            except Exception as e:
                last_error = e
                print(f"{model_name} failed: {e}")

        raise last_error


class ProductUpdate(BaseModel):
    brand: str | None = None
    product_name: str | None = None
    product_type: str | None = None
    ingredients: list[str] | None = None
    effectiveness_rating: int | None = None
    side_effects: list[str] | None = None
    is_current: bool | None = None
    usage_frequency: str | None = None
    

class ProductUpdater:
    def __init__(self):
        self.client = genai.Client(api_key=os.getenv('GOOGLE_API_KEY'))

    def extract(self, current_product, user_message):
        products_text = ""
        for product in current_product:
            products_text += f"""
            Brand: {product.brand or "N/A"}
            Product Name: {product.product_name or "N/A"}
            Product Type: {product.product_type or "N/A"}
            Ingredients: {product.ingredients or []}
            Usage Frequency: {product.usage_frequency or "N/A"}
            Effectiveness Rating: {
                product.effectiveness_rating
                if product.effectiveness_rating is not None
                else "N/A"
            }
            Side Effects: {product.side_effects or []}
            Is Current: {product.is_current}
            ---
        """        

        prompt = f"""
            You are LuminaSkin's product update assistant.

            The user wants to update their skincare product information.

            Current product information:
            {products_text}

            The user said:

            {user_message}

            Your task is to understand:
            1. Which product the user is referring to.
            2. What information they want to change.

            Return the COMPLETE resulting information for the product being updated.

            Rules:

            1. Identify which existing product the user is referring to using its brand,
            name, type, ingredients, or other available information.

            2. The returned product must be one of the products provided in the
            current product information.

            3. Do not change the brand or product name unless the user explicitly
            asks to change them.

            4. Only modify information that the user actually indicates.

            5. Preserve existing product information when the user does not mention
            changing it.

            6. If the user explicitly removes a piece of information, remove it.

            7. If the user explicitly adds a piece of information, add it.

            8. If the user replaces one piece of information with another, perform
            the replacement.

            9. Do not invent information.

            10. Return the complete resulting information for that product.

            11. Return all product fields for that product.
        """
        last_error = None

        for model_name in MODEL_NAMES:
            try:
                response = self.client.models.generate_content(
                    model=model_name,
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        response_mime_type="application/json",
                        response_schema=RoutineUpdate,
                        temperature=0.2,
                    )
                )

                return response.parsed

            except Exception as e:
                last_error = e
                print(f"{model_name} failed: {e}")

        raise last_erroe


class LifestyleUpdate(BaseModel):
    sleep_hours: float | None = None
    water_intake: float | None = None
    stress_level: str | None = None
    smoking: str | None = None
    alcohol_consumption: str | None = None
    exercise_frequency: str | None = None
    exercise_hours_per_week: float | None = None
    sun_exposure: str | None = None
    spf_usage: str | None = None


class LifestyleUpdater:

    def __init__(self):
        self.client = genai.Client(
            api_key=os.getenv("GOOGLE_API_KEY")
        )

    def extract(self, current_lifestyle, user_message):

        prompt = f"""
            You are LuminaSkin's lifestyle update assistant.

            The user wants to update their lifestyle information.

            Current lifestyle:

            Sleep Hours:
            {current_lifestyle.sleep_hours}

            Water Intake:
            {current_lifestyle.water_intake}

            Stress Level:
            {current_lifestyle.stress_level}

            Smoking:
            {current_lifestyle.smoking}

            Alcohol Consumption:
            {current_lifestyle.alcohol_consumption}

            Exercise Frequency:
            {current_lifestyle.exercise_frequency}

            Exercise Hours Per Week:
            {current_lifestyle.exercise_hours_per_week}

            Sun Exposure:
            {current_lifestyle.sun_exposure}

            SPF Usage:
            {current_lifestyle.spf_usage}

            The user said:

            {user_message}

            Your task is to understand what the user wants to change.

            Return the COMPLETE resulting lifestyle information.

            Rules:

            1. Only modify information that the user actually indicates.

            2. Preserve existing lifestyle information when the user
               does not mention changing it.

            3. If the user explicitly changes a value, update it.

            4. Do not invent information.

            5. Return the complete resulting lifestyle information.

            6. For choice fields, use ONLY these allowed values:

               Stress Level:
               - Low
               - Medium
               - High

               Smoking:
               - Never
               - Occasionally
               - Regularly

               Alcohol Consumption:
               - Never
               - Occasionally
               - Regularly

               Exercise Frequency:
               - None
               - 1-2/week
               - 3-5/week
               - Daily

               Sun Exposure:
               - Low
               - Medium
               - High

               SPF Usage:
               - Never
               - Sometimes
               - Always

            7. Do not change unrelated fields.

            8. Return numeric values as numbers.

            9. If the user does not mention a field, preserve its
               existing value.

            10. Do not invent values for fields the user did not mention.
        """

        last_error = None

        for model_name in MODEL_NAMES:
            try:
                response = self.client.models.generate_content(
                    model=model_name,
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        response_mime_type="application/json",
                        response_schema=RoutineUpdate,
                        temperature=0.2,
                    )
                )

                return response.parsed

            except Exception as e:
                last_error = e
                print(f"{model_name} failed: {e}")

        raise last_error


class ProfileUpdate(BaseModel):
    gender: str | None = None
    age: int | None = None
    country: str | None = None
    skin_goals: list[str] | None = None
    budget: str | None = None
    allergies: list[str] | None = None
    pregnancy_status: bool | None = None
    vegan_cruelty_free: bool | None = None

class ProfileUpdater:

    def __init__(self):
        self.client = genai.Client(
            api_key=os.getenv("GOOGLE_API_KEY")
        )

    def extract(self, current_profile, user_message):

        prompt = f"""
            You are LuminaSkin's profile update assistant.

            The user wants to update their personal skincare profile.

            Current profile:

            Gender:
            {current_profile.gender or "N/A"}

            Age:
            {current_profile.age if current_profile.age is not None else "N/A"}

            Country:
            {current_profile.country or "N/A"}

            Skin Goals:
            {current_profile.skin_goals or []}

            Budget:
            {current_profile.budget or "N/A"}

            Allergies:
            {current_profile.allergies or []}

            Pregnancy Status:
            {current_profile.pregnancy_status
                if current_profile.pregnancy_status is not None
                else "N/A"}

            Vegan / Cruelty Free:
            {current_profile.vegan_cruelty_free
                if current_profile.vegan_cruelty_free is not None
                else "N/A"}

            The user said:

            {user_message}

            Your task is to understand what the user wants to change.

            Return the COMPLETE resulting profile information.

            Rules:

            1. Only modify information that the user actually indicates.

            2. Preserve existing profile information when the user
               does not mention changing it.

            3. If the user explicitly changes a value, update it.

            4. If the user explicitly adds a skin goal or allergy,
               add it to the existing list.

            5. If the user explicitly removes a skin goal or allergy,
               remove it from the existing list.

            6. If the user explicitly replaces a value, perform
               the replacement.

            7. Do not invent information.

            8. Return the complete resulting profile information.

            9. Gender must use one of these values:

               - male
               - female
               - other
               - prefer_not_to_say

            10. Budget must use one of these values:

               - budget
               - mid
               - premium

            11. Pregnancy status must be true or false when specified.

            12. Vegan / cruelty-free must be true or false when specified.

            13. Do not change unrelated fields.

            14. Return age as a number.

            15. Return skin goals and allergies as lists of strings.
        """

        last_error = None

        for model_name in MODEL_NAMES:
            try:
                response = self.client.models.generate_content(
                    model=model_name,
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        response_mime_type="application/json",
                        response_schema=RoutineUpdate,
                        temperature=0.2,
                    )
                )

                return response.parsed

            except Exception as e:
                last_error = e
                print(f"{model_name} failed: {e}")

        raise last_error