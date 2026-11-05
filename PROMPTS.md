# PROMPTS.md

Where the AI was wrong, and what I did about it.

## 1. 3 Nov 2026: Choosing a stack
- **Asked:** Which stack should I use? I said I did not know.
- **AI got wrong / decided:** It suggested Node first, then switched to Django after I said I did not know.
- **Fix:** I chose Django because it has login and migrations built in, and I can explain it.
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
- **Fix:** I changed it to a small form with a POST button and a CSRF token. The view now only revokes on POST. Tested: after Revoke, the other user got 404 straight away.
- **Commit:** https://github.com/PujithaRajarapu/trustvault/commit/a437ae5

## 5. 4 Nov 2026: The access check was switched off (authorisation)
- **Asked:** Test that my tests catch a removed check.
- **What happened:** On my computer I turned off `if not allowed: raise Http404()` in `authorise()`. Two tests failed (`test_grant_allows_then_revoke_blocks` and one more). This proved the tests catch a removed check.
- **Fix:** I turned the check back on. The switched-off version was never committed. The correct guard code is in the commit below.
- **Commit:** https://github.com/PujithaRajarapu/trustvault/commit/a08280e

## 6. 5 Nov 2026: The AI told me to delete my own tests (authorisation tests)
- **Asked:** Tests proving that a stranger cannot download a document.
- **AI got wrong:** It told me to select all of `tests.py` and delete it without first asking what was in the file. My file already had 6 tests (53 lines), including real file downloads and a test that the audit chain detects tampering. They were deleted in the first commit below.
- **Fix:** I got the old file back from Git (`git show 357d5e8:vault/tests.py`) and merged my 6 tests with 7 new ones. All 13 tests pass.
- **Commits:** the mistake `5c9e838`, the fix `80742a2`

## 7. 5 Nov 2026: First replacement tests were too weak (access control)
- **Asked:** A small set of tests for the access check.
- **AI got wrong:** It only called `authorise()` directly with a fake file path. A page that forgot to call `authorise()` would still pass, and no real download was tested.
- **Fix:** I kept my own tests, which go through the real download and share pages with a real uploaded file, and added the stranger cases.
- **Commit:** `80742a2`

## Instructions I reused with the AI
- "One command at a time" (after pasted multi-line commands ran together).
- "Explain it in simple words" and "give me only one step".
- "Check against my real files before changing anything."
- AI tools I used: Claude (claude.ai).