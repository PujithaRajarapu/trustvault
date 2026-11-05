from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse

from .models import AuditLog, Document, Grant

PNG = b"\x89PNG\r\n\x1a\n" + b"0" * 50


class DeleteTests(TestCase):
    def setUp(self):
        User = get_user_model()
        self.owner = User.objects.create_user("owner", password="pass12345")
        self.friend = User.objects.create_user("friend", password="pass12345")
        self.stranger = User.objects.create_user("stranger", password="pass12345")
        self.doc = Document.objects.create(
            owner=self.owner,
            title="secret",
            file=SimpleUploadedFile("x.png", PNG),
            original_name="x.png",
            content_type="image/png",
            size_bytes=len(PNG),
        )
        self.delete_url = reverse("delete", args=[self.doc.id])
        self.download_url = reverse("download", args=[self.doc.id])

    def still_there(self):
        self.doc.refresh_from_db()
        return not self.doc.is_deleted

    def test_owner_can_delete_and_download_then_stops(self):
        self.client.login(username="owner", password="pass12345")
        self.assertEqual(self.client.post(self.delete_url).status_code, 302)
        self.assertFalse(self.still_there())
        self.assertEqual(self.client.get(self.download_url).status_code, 404)

    def test_stranger_cannot_delete(self):
        self.client.login(username="stranger", password="pass12345")
        self.assertEqual(self.client.post(self.delete_url).status_code, 404)
        self.assertTrue(self.still_there())

    def test_read_grant_cannot_delete(self):
        Grant.objects.create(document=self.doc, user=self.friend, level="read", granted_by=self.owner)
        self.client.login(username="friend", password="pass12345")
        self.assertEqual(self.client.post(self.delete_url).status_code, 404)
        self.assertTrue(self.still_there())

    def test_edit_grant_cannot_delete(self):
        Grant.objects.create(document=self.doc, user=self.friend, level="edit", granted_by=self.owner)
        self.client.login(username="friend", password="pass12345")
        self.assertEqual(self.client.post(self.delete_url).status_code, 404)
        self.assertTrue(self.still_there())

    def test_delete_needs_post(self):
        self.client.login(username="owner", password="pass12345")
        self.assertEqual(self.client.get(self.delete_url).status_code, 405)
        self.assertTrue(self.still_there())

    def test_anonymous_cannot_delete(self):
        self.assertEqual(self.client.post(self.delete_url).status_code, 302)
        self.assertTrue(self.still_there())

    def test_refused_delete_is_logged(self):
        self.client.login(username="stranger", password="pass12345")
        self.client.post(self.delete_url)
        self.assertTrue(AuditLog.objects.filter(action="delete", allowed=False).exists())