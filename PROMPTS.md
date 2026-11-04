# PROMPTS.md

Where the AI was wrong, and what I did about it.

## 1. 3 Nov 2026: Choosing a stack
- **Asked:** Which stack should I use? I said I did not know.
- **AI got wrong / decided:** It suggested Node first, then switched to Django after I said I did not know.
- **Fix:** I chose Django because it has login and migrations built in, and I can explain it.
- **Commit:** https://github.com/PujithaRajarapu/trustvault/commit/84cbcf

## 2. 3 Nov 2026: Audit log timestamp (audit trail)
- **Asked:** A hash-chained audit log.
- **AI got wrong:** It used `auto_now_add` for the timestamp. That fills the time only after saving, but the hash needs the time before saving.
- **Fix:** I changed it to `default=timezone.now` and made a new migration.
- **Commit:** https://github.com/PujithaRajarapu/trustvault/commit/a57a83a

## 3. 3 Nov 2026: Upload code did not match my models
- **Asked:** Upload code.
- **AI got wrong:** It wrote code for field names and an id type that my real `models.py` did not have (mine had different field names and an integer id).
- **Fix:** I pasted my real files and the AI rewrote the code to fit.
- **Commit:** https://github.com/PujithaRajarapu/trustvault/commit/fa9940f

## 4. 4 Nov 2026: Revoke button was a plain link (authorisation)
- **Asked:** A Revoke button in `share.html`.
- **AI got wrong:** It made it a plain link. A link sends a GET request, and my revoke view changes data, so another website could trigger it without me knowing.
- **Fix:** I changed it to a small form with a POST button and a CSRF token. The view now only revokes on POST. Tested: after Revoke, the other user got 404 straight away.
- **Commit:** https://github.com/PujithaRajarapu/trustvault/commit/a437ae5

## 5. 4 Nov 2026: The access check was switched off (authorisation)
- **Asked:** Test that my tests catch a removed check.
- **What happened:** I turned off `if not allowed: raise Http404()` in `authorise()`. Two tests failed (`test_grant_allows_then_revoke_blocks` and one more). This proved the tests catch a removed check.
- **Fix:** I turned the check back on and all 6 tests passed.
- **Commit:** https://github.com/PujithaRajarapu/trustvault/commit/b3c9d1e