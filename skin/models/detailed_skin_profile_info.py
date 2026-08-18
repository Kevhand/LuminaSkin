from django.db import models
from django.contrib.auth.models import User
import uuid
from skin.models.profile import SkinProfile



class Detailed_Information(models.Model):
    """
    Only if the user wants to provide more detailed information about their skin, they can fill this model. This is optional.
    Skin is an organ, and its condition is deeply tied to internal health. While pregnancy is a great catch for retinoid safety, experts need a broader medical context.
    """

    profile = models.OneToOneField(SkinProfile, on_delete=models.CASCADE)


    """
    - Current Medications: Birth control, antidepressants, or thyroid medications can drastically alter sebum production and skin behavior.
    - Medical Conditions: Polycystic Ovary Syndrome (PCOS), eczema, rosacea, psoriasis, or thyroid imbalances directly dictate which treatments will work.
    - Past Heavy Treatments: Has the user ever been on Accutane (Isotretinoin)? Have they had professional chemical peels or laser treatments recently?
    """
    medical_history = models.JSONField(default=list, null=True, blank=True)  # Store the medical history as a list of strings


    """
    While AI will scan for *concerns* (acne, wrinkles), the baseline *type* dictates the vehicle of the product (e.g., a gel vs. a heavy cream).

    - Self-Reported Skin Type: Oily, Dry, Combination, Normal, or Sensitive. (AI might misjudge "oily" if the user just applied a heavy moisturizer before the photo).
    - Ingredient Sensitivities: Beyond true medical allergies, do they know if specific common ingredients break them out or cause redness (e.g., "Niacinamide makes me flush" or "Coconut oil clogs my pores")?
    """

    baseline_skin_types = models.JSONField(default=list, null=True, blank=True)  # Store the baseline skin types as a list of stringss


    """
    A specialist will always look at external and internal triggers that skincare alone cannot fix.

    - **Dietary Triggers:** High dairy or high-glycemic (sugar) intake, which are heavily linked to hormonal acne.
    - **Climate/Weather:** Humid vs. dry climates change the need for humectants (like hyaluronic acid) versus occlusives (like shea butter).
    - **Water Quality:** Hard water can strip the skin and cause mineral buildup, worsening acne and dryness.
    """

    diet_environment_factors = models.JSONField(default=list, null=True, blank=True)  # Store the diet and environment factors as a list of strings

    """
    History of the Concen
    - **Onset:** How long has the primary concern been an issue? Did it start suddenly (suggesting a reaction or hormonal shift) or gradually?
    - **Previous Attempts:** What products or treatments have they tried for this specific issue that *failed*? (This prevents you from recommending something they already hate).
    """

    skin_concern_history = models.JSONField(default=list, null=True, blank=True)  # Store the skin concern history as a list of strings


