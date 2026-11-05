from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.views.decorators.http import require_POST

from .permissions import authorise


@login_required
@require_POST
def delete(request, doc_id):
    # "delete" is not in the read or edit lists, so only the owner passes.
    doc = authorise(request, doc_id, "delete")
    doc.is_deleted = True
    doc.save(update_fields=["is_deleted"])
    return redirect("home")