"""
Planner LLM.

Responsible for understanding the user's request and deciding
what information LuminaSkin needs before generating a response.

This module NEVER answers the user.

It only returns a structured execution plan.
"""


import json
import os

from dotenv import load_dotenv
from google import genai
from google.genai import types
from . import prompts
from typing import Literal
from pydantic import BaseModel

class ModulePlan(BaseModel):
    action: Literal[
        "chat",
        "report",
        "recommendation",
        "scan_analysis",
        "ingredient_analysis",
        "update_profile",
    ]

    modules: list[
        Literal[
            "profile",
            "lifestyle",
            "routine",
            "products",
            "latest_scan",
            "trends",
            "analytics_summary",
            "scan_history",

            "analytics_summary",
            "analytics_insights",
        ]
    ]

    field: str | None = None
    value: str | None = None

    confidence: float
    reason: str

GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
MODEL_NAMES = [
    "gemini-3.5-flash",
    "gemini-3.5-flash-lite",
]


class GeminiClient_module_selector:
    def __init__(self):
        self.client = genai.Client(api_key=GOOGLE_API_KEY)

    def generate(self, user_message):

        full_prompt = (
            prompts.prompt_module_selector
            + "\n\nUser Request:\n"
            + user_message
        )

        last_error = None

        for model_name in MODEL_NAMES:
            try:
                response = self.client.models.generate_content(
                    model=model_name,
                    contents=full_prompt,
                    config=types.GenerateContentConfig(
                        response_mime_type="application/json",
                        response_schema=ModulePlan,
                        temperature=0.2,
                    ),
                )

                return response.parsed

            except Exception as e:
                last_error = e
                print(f"{model_name} failed: {e}")

        raise last_error

load_dotenv()  # Load environment variables from .env file



class ModuleSelector:
    def __init__(self):
        self.client = GeminiClient_module_selector()

    def create_plan(self, user_input):
        response = self.client.generate(user_input)

        return response  # Convert the response to a Python dictionary