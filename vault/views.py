from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import render, redirect

from .audit import log_event
from .forms import UploadForm
from .models import Document, Profile
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
    return render(request, "home.html")


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