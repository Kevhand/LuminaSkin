import django.forms as forms

from skin.models import SkinProfile, Lifestyle, CurrentRoutine, Product, ProfileUpdateRequest


class SkinProfileForm(forms.ModelForm):


    skin_goals = forms.CharField(
        required=False,
        widget=forms.TextInput(
            attrs={
                "placeholder": "Acne, Brightening, Hydration"
            }
        )
    )

    allergies = forms.CharField(
        required=False,
        widget=forms.TextInput(
            attrs={
                "placeholder": "Fragrance, Niacinamide"
            }
        )
    )
    class Meta:
        model = SkinProfile

        fields = [
            "gender",
            "age",
            "country",
            "skin_goals",
            "budget",
            "allergies",
            "pregnancy_status",
            "vegan_cruelty_free",
        ]

        widgets = {
            "skin_goals": forms.TextInput(
                attrs={
                    "placeholder": "Acne, Brightening, Hydration"
                }
            ),
            "allergies": forms.TextInput(
                attrs={
                    "placeholder": "Fragrance, Niacinamide"
                }
            ),
        }
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if self.instance.pk:

            self.initial["skin_goals"] = ", ".join(
                self.instance.skin_goals or []
            )

            self.initial["allergies"] = ", ".join(
                self.instance.allergies or []
            )

    def clean_skin_goals(self):

        value = self.cleaned_data["skin_goals"]

        if isinstance(value, str):

            return [
                item.strip()
                for item in value.split(",")
                if item.strip()
            ]

        return value

    def clean_allergies(self):

        value = self.cleaned_data["allergies"]

        if isinstance(value, str):

            return [
                item.strip()
                for item in value.split(",")
                if item.strip()
            ]

        return value
class LifestyleForm(forms.ModelForm):

    sleep_hours = forms.FloatField(
        required=False,
        min_value=0,
        max_value=15,
        widget=forms.NumberInput(
            attrs={
                "min": 0,
                "max": 15,
                "step": 0.1,
                "placeholder": "Average sleep hours per night"
            }
        )
    )

    exercise_hours_per_week = forms.FloatField(
        required=False,
        min_value=0,
        max_value=168,
        widget=forms.NumberInput(
            attrs={
                "min": 0,
                "max": 168,
                "step": 0.1,
                "placeholder": "Average exercise hours per week"
            }
        )
    )

    water_intake = forms.FloatField(
        required=False,
        min_value=0,
        max_value=10,
        widget=forms.NumberInput(
            attrs={
                "min":0,
                "max":10,
                "step":0.1,
                "placeholder": "Average water intake in liters per day"
            }
        )
    )



    class Meta:
        model = Lifestyle

        fields = [
            "sleep_hours",
            "water_intake",
            "stress_level",
            "smoking",
            "alcohol_consumption",
            "exercise_frequency",
            "exercise_hours_per_week",
            "sun_exposure",
            "spf_usage",
        ]

class CurrentRoutineForm(forms.ModelForm):

    morning_routine = forms.CharField(
        required=False,
        widget=forms.TextInput(
            attrs={
                "placeholder": "Cleanser, Vitamin C, Moisturizer, SPF"
            }
        )
    )
    night_routine = forms.CharField(
        required=False,
        widget=forms.TextInput(
            attrs={
                "placeholder": "Cleanser, Retinol, Moisturizer"
            }
        )
    )

    class Meta:
        model = CurrentRoutine

        fields = [
            "morning_routine",
            "night_routine",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if self.instance.pk:
            self.initial["morning_routine"] = ", ".join(
                self.instance.morning_routine or []
            )

            self.initial["night_routine"] = ", ".join(
                self.instance.night_routine or []
            )

    def clean_morning_routine(self):

        value = self.cleaned_data["morning_routine"]

        if isinstance(value, str):
            return [
                item.strip()
                for item in value.split(",")
                if item.strip()
            ]

        return value

    def clean_night_routine(self):

        value = self.cleaned_data["night_routine"]

        if isinstance(value, str):
            return [
                item.strip()
                for item in value.split(",")
                if item.strip()
            ]

        return value
class ProductForm(forms.ModelForm):

    ingredients = forms.CharField(
        required=False,
        widget=forms.TextInput(
            attrs={
                "placeholder": "Niacinamide, Zinc, Glycerin"
            }
        )
    )
    side_effects = forms.CharField(
        required=False,
        widget=forms.TextInput(
            attrs={
                "placeholder": "Dryness, Irritation"
            }
        )
    )

    class Meta:
        model = Product

        fields = [
            "brand",
            "product_name",
            "product_type",
            "ingredients",
            "usage_frequency",
            "effectiveness_rating",
            "side_effects",
            "is_current",
        ]


        widgets = {
            "ingredients": forms.TextInput(
                attrs={
                    "placeholder": "Niacinamide, Zinc, Glycerin"
                }
            ),
            "side_effects": forms.TextInput(
                attrs={
                    "placeholder": "Dryness, Irritation"
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if self.instance.pk:

            self.initial["ingredients"] = ", ".join(
                self.instance.ingredients or []
            )

            self.initial["side_effects"] = ", ".join(
                self.instance.side_effects or []
            )

    def clean_ingredients(self):

        value = self.cleaned_data["ingredients"]

        if isinstance(value, str):

            return [
                item.strip()
                for item in value.split(",")
                if item.strip()
            ]

        return value

    def clean_side_effects(self):

        value = self.cleaned_data["side_effects"]

        if isinstance(value, str):

            return [
                item.strip()
                for item in value.split(",")
                if item.strip()
            ]

        return value

class ProfileUpdateRequestForm(forms.ModelForm):
    class Meta:
        model = ProfileUpdateRequest

        fields = [
            "field",
            "old_value",
            "new_value",
            "reason",
            "approved",
            
        ]