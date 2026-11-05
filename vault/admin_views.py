from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.shortcuts import render

from .audit import log_event, verify_chain
from .models import AuditLog, Profile


def is_admin(user):
    if not user.is_authenticated:
        return False
    profile = Profile.objects.filter(user=user).first()
    return profile is not None and profile.role == "admin"


@login_required
def activity(request):
    if not is_admin(request.user):
        log_event(request.user, "admin_page", None, False, "not an administrator")
        raise Http404()

    entries = AuditLog.objects.order_by("-id")
    if request.GET.get("denied") == "1":
        entries = entries.filter(allowed=False)
    action = request.GET.get("action", "")
    if action:
        entries = entries.filter(action=action)

    chain_ok, broken_id = verify_chain()
    return render(request, "activity.html", {
        "entries": entries[:200],
        "chain_ok": chain_ok,
        "broken_id": broken_id,
        "denied_total": AuditLog.objects.filter(allowed=False).count(),
        "total": AuditLog.objects.count(),
    })