import uuid

from django.db import models
from django.contrib.auth.models import User
from . import Scan


ROLE_CHOICES = [
    ("user", "User"),
    ("assistant", "Assistant"),
    ("system", "System"),
]


class ChatSession(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='chat_sessions')

    initial_scan = models.ForeignKey(Scan, on_delete=models.SET_NULL, null=True, blank=True)

    title = models.CharField(max_length=255, default="New Chat Session")
    session_id = models.UUIDField(unique=True, default=uuid.uuid4, editable=False, db_index=True)

    conversation_summary = models.TextField(blank=True, default="")


    metadata = models.JSONField(default=dict, blank=True)

    is_active = models.BooleanField(default=True)

    is_deleted = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


    class Meta:
        ordering = ['-updated_at']

    def __str__(self):
        return f"{self.user.username} - {self.title}"


MESSAGE_TYPES = [
    ("chat", "Chat"),
    ("report", "Report"),
    ("recommendation", "Recommendation"),
    ("scan_analysis", "Scan Analysis"),
    ("ingredient_analysis", "Ingredient Analysis"),

]


class ChatMessage(models.Model):
    session = models.ForeignKey(ChatSession, on_delete=models.CASCADE, related_name='messages')

    role = models.CharField(max_length=10, choices=ROLE_CHOICES)

    content = models.TextField()

    message_type = models.CharField(max_length=20, default="text", choices=MESSAGE_TYPES)  

    created_at = models.DateTimeField(auto_now_add=True)

    updated_at = models.DateTimeField(auto_now=True)


    metadata = models.JSONField(default=dict, blank=True)

    def __str__(self):
        return f"{self.role}: {self.content[:40]}"

    class Meta:
        ordering = ['created_at']

  