import hashlib
from datetime import timezone as dt_timezone

from django.db import transaction
from django.utils import timezone

from .models import AuditLog

START = "0" * 64  # the "previous hash" of the very first entry


def make_hash(prev_hash, actor, action, document_id, title, allowed, detail, when):
    when_text = when.astimezone(dt_timezone.utc).isoformat()
    text = "|".join([
        prev_hash, actor, action, str(document_id), title,
        str(allowed), detail, when_text,
    ])
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def log_event(user, action, document=None, allowed=True, detail=""):
    """Add one new line to the log. Each line remembers the one before it."""
    actor = user.username if (user is not None and user.is_authenticated) else "anonymous"
    doc_id = document.id if document else None
    title = document.title if document else ""
    detail = detail[:300]

    with transaction.atomic():
        last = AuditLog.objects.order_by("-id").first()
        prev_hash = last.entry_hash if last else START
        now = timezone.now()
        entry_hash = make_hash(prev_hash, actor, action, doc_id, title, allowed, detail, now)
        return AuditLog.objects.create(
            timestamp=now, actor=actor, action=action,
            document_id=doc_id, document_title=title,
            allowed=allowed, detail=detail,
            prev_hash=prev_hash, entry_hash=entry_hash,
        )


def verify_chain():
    """Check the whole log. Returns (True, None) if fine, or (False, id of the broken line)."""
    prev_hash = START
    for e in AuditLog.objects.order_by("id"):
        expected = make_hash(
            prev_hash, e.actor, e.action, e.document_id, e.document_title,
            e.allowed, e.detail, e.timestamp,
        )
        if e.prev_hash != prev_hash or e.entry_hash != expected:
            return False, e.id
        prev_hash = e.entry_hash
    return True, None