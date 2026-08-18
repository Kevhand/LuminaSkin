from django.db import models
from django.contrib.auth.models import User
import uuid


class AIProfileSnapshot(models.Model):

    user = models.OneToOneField(User, on_delete=models.CASCADE)

    context = models.JSONField()

    ai_report = models.TextField()

    generated_at = models.DateTimeField(auto_now=True)

    