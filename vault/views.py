from django.contrib.auth import get_user_model, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import render, redirect
from django.http import FileResponse
from .permissions import authorise

from .audit import log_event
from .forms import UploadForm
from .models import Document, Grant, Profile
from .validators import clean_name


def register(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            Profile.objects.create(user=user, role="owner")
            login(request, user)
            log_event(user, "register", None, True)
            return redirect("home")
    else:
        form = UserCreationForm()
    return render(request, "registration/register.html", {"form": form})


@login_required
def home(request):
    docs = Document.objects.filter(owner=request.user, is_deleted=False).order_by("-uploaded_at")
    shared = Grant.objects.filter(
        user=request.user, document__is_deleted=False
    ).select_related("document", "document__owner")
    return render(request, "home.html", {"docs": docs, "shared": shared})


@login_required
def upload(request):
    if request.method == "POST":
        form = UploadForm(request.POST, request.FILES)
        if form.is_valid():
            f = form.cleaned_data["file"]
            doc = Document.objects.create(
                owner=request.user,
                title=form.cleaned_data["title"],
                category=form.cleaned_data["category"],
                file=f,
                original_name=clean_name(f.name),
                content_type=form.detected_type,
                size_bytes=f.size,
            )
            log_event(request.user, "upload", doc, True)
            return redirect("home")
    else:
        form = UploadForm()
    return render(request, "upload.html", {"form": form})


@login_required
def download(request, doc_id):
    doc = authorise(request, doc_id, "download")
    response = FileResponse(
        doc.file.open("rb"),
        as_attachment=True,
        filename=doc.original_name,
        content_type=doc.content_type,
    )
    response["X-Content-Type-Options"] = "nosniff"
    return response


@login_required
def share(request, doc_id):
    doc = authorise(request, doc_id, "share")
    message = ""
    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        level = request.POST.get("level", "read")
        if level not in ("read", "edit"):
            level = "read"
        target = get_user_model().objects.filter(username=username).first()
        if target is None or target.id == request.user.id:
            message = "Could not share with that user."
        else:
            Grant.objects.update_or_create(
                document=doc,
                user=target,
                defaults={"level": level, "granted_by": request.user},
            )
            log_event(request.user, "grant", doc, True, "to " + target.username + " (" + level + ")")
            message = "Shared with " + target.username + "."
    grants = Grant.objects.filter(document=doc).select_related("user")
    return render(request, "share.html", {"doc": doc, "grants": grants, "message": message})


@login_required
def revoke(request, doc_id, user_id):
    doc = authorise(request, doc_id, "revoke")
    if request.method == "POST":
        grant = Grant.objects.filter(document=doc, user_id=user_id).first()
        if grant is not None:
            name = grant.user.username
            grant.delete()
            log_event(request.user, "revoke", doc, True, "from " + name)
    return redirect("share", doc_id=doc.id)