from django.http import Http404

from .audit import log_event
from .models import Document, Grant

# What each permission level is allowed to do.
# The owner of a document can do everything, so the owner is not listed here.
READ_ACTIONS = {"view", "download"}
EDIT_ACTIONS = {"view", "download", "edit"}
# share, revoke and delete are not listed, so only the owner can do them.


def authorise(request, doc_id, action):
    """THE ONE PLACE where we decide if someone can touch a document.
    Every page that uses a document must call this first.
    If the answer is no, it writes the refusal in the audit log and shows a 404 page.
    A 404 means a stranger cannot even tell if the document exists."""
    user = request.user
    doc = Document.objects.filter(id=doc_id, is_deleted=False).first()

    allowed = False
    if doc is not None and user.is_authenticated:
        if doc.owner_id == user.id:
            allowed = True
        else:
            # Look in the database every single time, so removing access works at once.
            grant = Grant.objects.filter(document=doc, user=user).first()
            if grant is not None:
                if grant.level == "read" and action in READ_ACTIONS:
                    allowed = True
                elif grant.level == "edit" and action in EDIT_ACTIONS:
                    allowed = True

    detail = "" if doc is not None else "document not found: " + str(doc_id)
    log_event(user, action, doc, allowed, detail)

    if not allowed:
        raise Http404()
    return doc