from django.db import models
from django.contrib.auth.models import User
import uuid



def orignial_image_upload_path(instance, filename):
    return f"user/{instance.user.id}/scans/{instance.scan_id}/original/{filename}"

def resized_image_upload_path(instance, filename):
    return f"user/{instance.user.id}/scans/{instance.scan_id}/resized/{filename}"



class Scan(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    scan_id = models.UUIDField(unique=True, default=uuid.uuid4, editable=False)

    overall_score = models.FloatField(null=True, blank=True)

    skin_age = models.IntegerField(null=True, blank=True)

    skin_type = models.JSONField(default=dict, null=True, blank=True)  # Store skin type details as JSON

    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)

    selected_concern = models.JSONField(default=list)  # Store the skin concerns and their details as JSON

    original_image = models.ImageField(upload_to=orignial_image_upload_path, null=True, blank=True)

    resized_image = models.ImageField(upload_to=resized_image_upload_path, null=True, blank=True)


def mask_image_upload_path(instance, filename):
    return f"user/{instance.scan.user.id}/scans/{instance.scan.scan_id}/masks/{filename}"

def overlay_image_upload_path(instance, filename):
    return f"user/{instance.scan.user.id}/scans/{instance.scan.scan_id}/overlays/{filename}"



STATUS_CHOICES = [
    ("pending", "Pending"),
    ("completed", "Completed"),
    ("failed", "Failed"),
]

class ScanResult(models.Model):
    
    scan = models.ForeignKey(Scan, on_delete=models.CASCADE, related_name='results')

    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='pending')

    skin_concern = models.CharField(max_length=100)

    mask_image = models.ImageField(upload_to=mask_image_upload_path, null=True, blank=True)

    ui_score = models.FloatField(null=True, blank=True)
    raw_score = models.FloatField(null=True, blank=True)

    overlay_image = models.ImageField(upload_to=overlay_image_upload_path, null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
