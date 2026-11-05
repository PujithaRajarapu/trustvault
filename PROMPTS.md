# PROMPTS.md

Where the AI was wrong, and what I did about it.

## 1. 3 Nov 2026: Choosing a stack (a decision, not a mistake)
- **Asked:** Which stack should I use? I said I did not know.
- **What happened:** The AI first suggested Node, then picked Django after I said I did not know.
- **Decision:** I went with Django because it has login and migrations built in, and I can explain it.
- **Commit:** https://github.com/PujithaRajarapu/trustvault/commit/84cbbcf

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
- **Fix:** I changed it to a small form with a POST button and a CSRF token. The view only revokes on POST. Tested: after Revoke, the other user got 404 straight away.
- **Commit:** https://github.com/PujithaRajarapu/trustvault/commit/a437ae5

## 5. 4 Nov 2026: Proving my tests catch a removed access check (authorisation)
- **Asked:** How do I know my tests would fail if the check were removed?
- **What I did:** On my computer I commented out `if not allowed: raise Http404()` in `authorise()`. Three tests failed (`test_stranger_gets_404`, `test_grant_allows_then_revoke_blocks`, `test_read_grant_cannot_share`). I then removed the `#` marks and all tests passed again.
- **Result:** The tests really do catch a removed check. The switched-off version was never committed.
- **Commit with the tests:** https://github.com/PujithaRajarapu/trustvault/commit/80742a2
## 6. 5 Nov 2026: A rewrite of my tests removed some of them (authorisation tests)
- **Asked:** Tests proving that a stranger cannot download a document and that revoke works at once.
- **What went wrong:** The new version of tests.py (commit 5c9e838) removed 53 lines and added 29. Some of my earlier tests were lost.
- **Fix:** I restored my earlier tests and added more stranger and revoke tests in commit 80742a2. All tests pass.
- **Commits:** 5c9e838 (the problem), 80742a2 (the fix)