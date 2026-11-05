import os

from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand

from vault.models import Document, Grant, Profile

# A tiny valid PNG image, used as the sample document.
PNG = (
    b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06"
    b"\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\rIDATx\x9cc\xf8\xff\xff?\x00\x05\xfe"
    b"\x02\xfe\xa7\x9a\xa0\xa0\x00\x00\x00\x00IEND\xaeB`\x82"
)


class Command(BaseCommand):
    help = "Create demo users and a sample document (safe to run many times)."

    def handle(self, *args, **options):
        User = get_user_model()
        password = os.environ.get("DEMO_PASSWORD")
        if not password:
            self.stdout.write("DEMO_PASSWORD is not set, so no demo users were created.")
            return

        def make_user(name, role):
            user, created = User.objects.get_or_create(username=name)
            if created:
                user.set_password(password)
                user.save()
            Profile.objects.update_or_create(user=user, defaults={"role": role})
            return user

        make_user("demo_admin", "admin")
        owner = make_user("demo_owner", "owner")
        viewer = make_user("demo_viewer", "viewer")
        make_user("demo_stranger", "viewer")

        doc = Document.objects.filter(owner=owner, title="Sample report").first()
        if doc is None:
            doc = Document(
                owner=owner, title="Sample report", category="demo",
                original_name="sample.png", content_type="image/png", size_bytes=len(PNG),
            )
            doc.file.save("sample.png", ContentFile(PNG), save=True)
        elif not doc.file or not doc.file.storage.exists(doc.file.name):
            doc.file.save("sample.png", ContentFile(PNG), save=True)

        Grant.objects.get_or_create(
            document=doc, user=viewer, defaults={"level": "read", "granted_by": owner}
        )
        self.stdout.write("Demo users and sample document are ready.")