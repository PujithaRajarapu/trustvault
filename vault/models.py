from django.conf import settings
import uuid
from django.db import models
from django.utils import timezone


class Profile(models.Model):
    """Which of the three roles a user has."""
    ROLES = [("admin", "Administrator"), ("owner", "Owner"), ("viewer", "Viewer")]
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    role = models.CharField(max_length=10, choices=ROLES, default="viewer")

def private_path(instance, filename):
    # The saved file gets a random name. The user's own filename is never used on disk.
    return uuid.uuid4().hex

class Document(models.Model):
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    category = models.CharField(max_length=50, blank=True)
    file = models.FileField(upload_to=private_path)
    original_name = models.CharField(max_length=100, default="file")
    content_type = models.CharField(max_length=100, default="")
    size_bytes = models.PositiveBigIntegerField(default=0)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    is_deleted = models.BooleanField(default=False)


class Grant(models.Model):
    """One row = one person is allowed Read or Edit on one document.
    No row means no access."""
    LEVELS = [("read", "Read"), ("edit", "Edit")]
    document = models.ForeignKey(Document, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    level = models.CharField(max_length=4, choices=LEVELS)
    granted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name="+"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("document", "user")


class AuditLog(models.Model):
    """Append-only record of who did what, including refused attempts."""
    timestamp = models.DateTimeField(default=timezone.now, editable=False)
    actor = models.CharField(max_length=150)
    action = models.CharField(max_length=50)
    document_id = models.IntegerField(null=True)
    document_title = models.CharField(max_length=200, blank=True)
    allowed = models.BooleanField()
    detail = models.CharField(max_length=300, blank=True)
    prev_hash = models.CharField(max_length=64, blank=True)
    entry_hash = models.CharField(max_length=64, blank=True)