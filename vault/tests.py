from django.contrib.auth import get_user_model
from django.http import Http404
from django.test import RequestFactory, TestCase

from .models import Document, Grant
from .permissions import authorise

User = get_user_model()


class AccessTests(TestCase):
    def setUp(self):
        self.owner = User.objects.create_user("owner1", password="pw-12345-xyz")
        self.other = User.objects.create_user("other1", password="pw-12345-xyz")
        self.doc = Document.objects.create(
            owner=self.owner, title="secret", category="",
            file="docs/fake.txt", original_name="fake.txt",
            content_type="text/plain", size_bytes=1,
        )

    def request_for(self, user):
        request = RequestFactory().get("/x")
        request.user = user
        return request

    def test_owner_is_allowed(self):
        authorise(self.request_for(self.owner), self.doc.id, "download")

    def test_stranger_is_refused(self):
        with self.assertRaises(Http404):
            authorise(self.request_for(self.other), self.doc.id, "download")

    def test_revoked_access_stops_at_once(self):
        grant = Grant.objects.create(document=self.doc, user=self.other, level="read")
        authorise(self.request_for(self.other), self.doc.id, "download")
        grant.delete()
        with self.assertRaises(Http404):
            authorise(self.request_for(self.other), self.doc.id, "download")