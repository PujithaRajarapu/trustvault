3 Nov 2026: Asked the AI for a stack. I said I did not know, and it picked Django.

3 Nov 2026: The AI gave me a timestamp field that was wrong for the audit log. I changed it to default=timezone.now. Commit: a57a83a

3 Nov 2026: The AI wrote upload code that did not match my real models.py, which had different field names and an integer id. I pasted my real files and the AI rewrote the code to fit. Commit: fa9940f

4 Nov 2026: The AI first made the Revoke button in share.html a plain link. But my revoke view changes data, and a link sends a GET request, which another website could trigger without me knowing. I changed it to a small form with a POST button and a CSRF token, and the view only revokes on POST. Tested: after Revoke, the other user got 404 straight away. Commit: a437ae5