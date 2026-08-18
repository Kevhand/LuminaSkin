from django.db import models
from django.contrib.auth.models import User
import uuid



class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    profile_picture = models.ImageField(upload_to='profile_pictures/', null=True, blank=True)

    mobile_number = models.CharField(max_length=15, null=True, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)

    def __str__(self):
        return self.user.username


budget_choices = [
    ('budget', 'Budget'),
    ('mid', 'Mid Range'),
    ('premium', 'Premium'),
]

gender_choices = [
    ('male', 'Male'),
    ('female', 'Female'),
    ('other', 'Other'),
    ('prefer_not_to_say', 'Prefer not to say'),
]



class SkinProfile(models.Model):
    #Basic user information
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    gender = models.CharField(max_length=20, choices=gender_choices, null=True, blank=True)
    age = models.IntegerField(null=True, blank=True)
    country = models.CharField(max_length=100, null=True, blank=True) # For Product Recommendations based on location

    #Goals
    skin_goals = models.JSONField(default=list, null=True, blank=True)  # Store the skin goals as a list of strings

    #Preferences
    budget = models.CharField(max_length=10, null=True, blank=True, choices=budget_choices)  # Budget for skincare products
    allergies = models.JSONField(default=list, null=True, blank=True)  # Store the allergies as a list of strings

    pregnancy_status = models.BooleanField(null=True, blank=True)  # True if pregnant, False if not, None if unknown

    vegan_cruelty_free = models.BooleanField(null=True, blank=True)  # True if vegan/cruelty-free, False if not, None if unknown


    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


    @property
    def profile_exists(self):
        return any([
            self.gender,
            self.age,
            self.country,
            self.skin_goals,
            self.budget,
            self.allergies,
            self.pregnancy_status is not None,
            self.vegan_cruelty_free is not None,
        ])


    @property
    def completion_percentage(self):
        total_fields = 8  # Total number of fields to check
        filled_fields = sum([
            bool(self.gender),
            bool(self.age),
            bool(self.country),
            bool(self.skin_goals),
            bool(self.budget),
            bool(self.allergies),
            self.pregnancy_status is not None,
            self.vegan_cruelty_free is not None,
        ])
        return round((filled_fields / total_fields) * 100)





stress_level_choices = [
    ('Low', 'Low'),
    ('Medium', 'Medium'),
    ('High', 'High'),
]

smoking_choices = [
    ('Never', 'Never'),
    ('Occasionally', 'Occasionally'),
    ('Regularly', 'Regularly'),
]

alcohol_consumption_choices = [
    ('Never', 'Never'),
    ('Occasionally', 'Occasionally'),
    ('Regularly', 'Regularly'),
]

exercise_frequency_choices = [
    ('None', 'None'),
    ('1-2/week', '1-2 times/week'),
    ('3-5/week', '3-5 times/week'),
    ('Daily', 'Daily'),
]

sun_exposure_choices = [
    ('Low', 'Low'),
    ('Medium', 'Medium'),
    ('High', 'High'),
]

spf_usage_choices = [
    ('Never', 'Never'),
    ('Sometimes', 'Sometimes'),
    ('Always', 'Always'),
]

class Lifestyle(models.Model):
    profile = models.OneToOneField(SkinProfile, on_delete=models.CASCADE)

    sleep_hours = models.FloatField(null=True, blank=True)  # Average sleep hours per night

    water_intake = models.FloatField(null=True, blank=True)  # Average water intake in liters per day

    stress_level = models.CharField(max_length=50, null=True, blank=True, choices=stress_level_choices)  # e.g., Low, Medium, High

    smoking = models.CharField(max_length=50, null=True, blank=True, choices=smoking_choices)  # e.g., Never, Occasionally, Regularly


    alcohol_consumption = models.CharField(max_length=50, null=True, blank=True, choices=alcohol_consumption_choices)  # e.g., Never, Occasionally, Regularly


    exercise_frequency = models.CharField(max_length=50, null=True, blank=True, choices=exercise_frequency_choices)  # e.g., None, Occasional, Regular

    exercise_hours_per_week = models.FloatField(null=True, blank=True)  # Average exercise hours per week

    sun_exposure = models.CharField(max_length=50, null=True, blank=True, choices=sun_exposure_choices)  # e.g., Low, Medium, High

    spf_usage = models.CharField(max_length=50, null=True, blank=True, choices=spf_usage_choices)  # e.g., Never, Sometimes, Always


    @property
    def lifestyle_exists(self):
        return any([
            self.sleep_hours is not None,
            self.water_intake is not None,
            bool(self.stress_level),
            bool(self.smoking),
            bool(self.alcohol_consumption),
            bool(self.exercise_frequency),
            self.exercise_hours_per_week is not None,
            bool(self.sun_exposure),
            bool(self.spf_usage),
        ])

    @property
    def completion_percentage(self):
        total_fields = 9  # Total number of fields to check
        filled_fields = sum([
            self.sleep_hours is not None,
            self.water_intake is not None,
            bool(self.stress_level),
            bool(self.smoking),
            bool(self.alcohol_consumption),
            bool(self.exercise_frequency),
            self.exercise_hours_per_week is not None,
            bool(self.sun_exposure),
            bool(self.spf_usage),
        ])
        return round((filled_fields / total_fields) * 100)





class CurrentRoutine(models.Model):
    profile = models.OneToOneField(SkinProfile, on_delete=models.CASCADE)

    morning_routine = models.JSONField(default=list, null=True, blank=True)  # Store the morning routine as a list of strings

    night_routine = models.JSONField(default=list, null=True, blank=True)  # Store the night routine as a list of strings

    @property
    def routine_exists(self):
        return any([
            bool(self.morning_routine),
            bool(self.night_routine),
        ])

    @property
    def completion_percentage(self):
        total_fields = 2  # Total number of fields to check
        filled_fields = sum([
            bool(self.morning_routine),
            bool(self.night_routine),
        ])
        return round((filled_fields / total_fields) * 100)


class Product(models.Model):
    profile = models.ForeignKey(SkinProfile, on_delete=models.CASCADE)

    brand = models.CharField(max_length=255)

    product_name = models.CharField(max_length=255)

    product_type = models.CharField(max_length=100)  # e.g., Cleanser, Moisturizer, Serum, etc.

    ingredients = models.JSONField(default=list, null=True, blank=True)  # Store the ingredients as a list of strings

    usage_frequency = models.CharField(max_length=100, null=True, blank=True)  # e.g., Daily, Weekly, As needed

    effectiveness_rating = models.IntegerField(null=True, blank=True)  # User's rating of the product's effectiveness (1-5)

    side_effects = models.JSONField(default=list, null=True, blank=True)  # Store any side effects experienced as a list of strings

    is_current = models.BooleanField(default=True)


    @property
    def completion_percentage(self):
        total_fields = 7  # Total number of fields to check
        filled_fields = sum([
            bool(self.brand),
            bool(self.product_name),
            bool(self.product_type),
            bool(self.ingredients),
            bool(self.usage_frequency),
            self.effectiveness_rating is not None,
            bool(self.side_effects),
        ])
        return round((filled_fields / total_fields) * 100)


class ProfileUpdateRequest(models.Model):

    profile = models.ForeignKey(SkinProfile, on_delete=models.CASCADE)

    field = models.CharField(max_length=100)

    old_value = models.JSONField()

    new_value = models.JSONField()

    reason = models.TextField()

    approved = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)