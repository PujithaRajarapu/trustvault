from django import forms
from django.core.exceptions import ValidationError

from .validators import MAX_SIZE, sniff_type


class UploadForm(forms.Form):
    title = forms.CharField(max_length=200)
    category = forms.CharField(max_length=50, required=False)
    file = forms.FileField()

    def clean_file(self):
        f = self.cleaned_data["file"]
        if f.size == 0 or f.size > MAX_SIZE:
            raise ValidationError("File must be between 1 byte and 5 MB.")
        head = f.read(16)
        f.seek(0)
        kind = sniff_type(head)
        if kind is None:
            raise ValidationError("Only PDF, PNG and JPEG files are allowed.")
        self.detected_type = kind
        return f