from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse

from .audit import verify_chain
from .models import AuditLog, Document, Grant

PNG = b"\x89PNG\r\n\x1a\n" + b"0" * 50


class AccessTests(TestCase):
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
        self.url = reverse("download", args=[self.doc.id])

    def test_owner_can_download(self):
        self.client.login(username="owner", password="pass12345")
        self.assertEqual(self.client.get(self.url).status_code, 200)

    def test_stranger_gets_404(self):
        self.client.login(username="stranger", password="pass12345")
        self.assertEqual(self.client.get(self.url).status_code, 404)

    def test_grant_allows_then_revoke_blocks(self):
        Grant.objects.create(document=self.doc, user=self.friend, level="read", granted_by=self.owner)
        self.client.login(username="friend", password="pass12345")
        self.assertEqual(self.client.get(self.url).status_code, 200)
        Grant.objects.filter(document=self.doc, user=self.friend).delete()
        self.assertEqual(self.client.get(self.url).status_code, 404)

    def test_read_grant_cannot_share(self):
        Grant.objects.create(document=self.doc, user=self.friend, level="read", granted_by=self.owner)
        self.client.login(username="friend", password="pass12345")
        resp = self.client.get(reverse("share", args=[self.doc.id]))
        self.assertEqual(resp.status_code, 404)

    def test_refusal_is_logged(self):
        self.client.login(username="stranger", password="pass12345")
        self.client.get(self.url)
        self.assertTrue(AuditLog.objects.filter(action="download", allowed=False).exists())

    def test_audit_chain_detects_tampering(self):
        self.client.login(username="owner", password="pass12345")
        self.client.get(self.url)
        self.client.get(self.url)
        self.assertEqual(verify_chain()[0], True)
        first = AuditLog.objects.order_by("id").first()
        first.detail = "changed"
        first.save()
        self.assertEqual(verify_chain()[0], False)

    # ---- new tests ----

    def test_anonymous_is_sent_to_login(self):
        self.assertEqual(self.client.get(self.url).status_code, 302)

    def test_edit_grant_cannot_share(self):
        Grant.objects.create(document=self.doc, user=self.friend, level="edit", granted_by=self.owner)
        self.client.login(username="friend", password="pass12345")
        resp = self.client.get(reverse("share", args=[self.doc.id]))
        self.assertEqual(resp.status_code, 404)

    def test_stranger_cannot_open_share_page(self):
        self.client.login(username="stranger", password="pass12345")
        resp = self.client.get(reverse("share", args=[self.doc.id]))
        self.assertEqual(resp.status_code, 404)

    def test_stranger_cannot_grant_themselves_access(self):
        self.client.login(username="stranger", password="pass12345")
        resp = self.client.post(
            reverse("share", args=[self.doc.id]),
            {"username": "stranger", "level": "edit"},
        )
        self.assertEqual(resp.status_code, 404)
        self.assertFalse(Grant.objects.filter(document=self.doc, user=self.stranger).exists())

    def test_stranger_cannot_revoke_someone_elses_grant(self):
        Grant.objects.create(document=self.doc, user=self.friend, level="read", granted_by=self.owner)
        self.client.login(username="stranger", password="pass12345")
        self.client.post(reverse("revoke", args=[self.doc.id, self.friend.id]))
        self.assertTrue(Grant.objects.filter(document=self.doc, user=self.friend).exists())

    def test_deleted_document_is_refused_even_for_owner(self):
        self.doc.is_deleted = True
        self.doc.save()
        self.client.login(username="owner", password="pass12345")
        self.assertEqual(self.client.get(self.url).status_code, 404)

    def test_missing_document_gives_404(self):
        self.client.login(username="owner", password="pass12345")
        resp = self.client.get(reverse("download", args=[999999]))
        self.assertEqual(resp.status_code, 404)