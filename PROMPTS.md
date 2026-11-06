# PROMPTS.md

Where the AI was wrong, and what I did about it.

AI tools used: Claude (claude.ai), in chat, to guide me step by step. I also used ChatGPT and DeepSeek after building, for suggestions and code review (see entry 8).

## 1. 3 Nov 2026: Choosing a stack (a decision, not a mistake)
- **Asked:** Which stack should I use? I said I did not know.
- **What happened:** The AI first suggested Node with Express, which I did not know. When I said I knew some Python, it picked Django.
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
- **What I did:** On my computer I switched off `if not allowed: raise Http404()` in `authorise()`. Several tests failed, including `test_stranger_gets_404`, `test_grant_allows_then_revoke_blocks` and `test_read_grant_cannot_share`. I then put the check back and all tests passed again.
- **Result:** The tests really do catch a removed check. The switched-off version was never committed.
- **Commits:** https://github.com/PujithaRajarapu/trustvault/commit/9234a5a (check restored, tests pass) and https://github.com/PujithaRajarapu/trustvault/commit/80742a2 (the tests)

## 6. 5 Nov 2026: The AI told me to delete my own tests (authorisation tests)
- **Asked:** Tests proving that a stranger cannot download a document and that revoke works at once.
- **AI got wrong:** It told me to select all of `tests.py` and delete it, without checking what was in it. My file already had 6 tests (53 lines), including real file downloads and a test that the audit chain detects tampering. They were removed in commit 5c9e838.
- **Fix:** I got the old file back from Git (`git show 357d5e8:vault/tests.py`) and merged it with 7 new tests: anonymous user, edit grant cannot share, stranger cannot open the share page, stranger cannot grant themselves access, stranger cannot revoke, deleted document, missing document. All 13 tests pass.
- **Commits:** https://github.com/PujithaRajarapu/trustvault/commit/5c9e838 (the problem) and https://github.com/PujithaRajarapu/trustvault/commit/80742a2 (the fix)

## 7. 5 Nov 2026: First replacement tests were too weak (access control)
- **Asked:** A small set of tests for the access check.
- **AI got wrong:** It only called `authorise()` directly with a fake file path. A page that forgot to call `authorise()` would still pass, and no real download was tested.
- **Fix:** I kept my own tests, which go through the real download and share pages with a real uploaded file, and added the stranger cases.
- **Commit:** https://github.com/PujithaRajarapu/trustvault/commit/80742a2

## 8. 5 Nov 2026: Unreviewed edits from other AIs (authorisation and audit)
- **Asked:** I asked ChatGPT and DeepSeek to improve my code.
- **AI got wrong:** They returned about 300 lines of changes across `permissions.py`, `models.py`, `views.py`, `admin_views.py` and `settings.py`, plus a new database migration that changed the audit log and grants tables. They rewrote my `authorise()` function and removed my comments. One change made an unknown action return 404 without writing it to the audit log, which breaks my rule that refused attempts are always logged.
- **Why it mattered:** I had not read or tested the edits. A table migration one day before the deadline could break my live database, which already holds data and an audit chain.
- **Fix:** I did not ship them. I saved them aside in a git stash (not committed), confirmed that my pushed version passes all 22 tests, and kept my own code. The version I kept is this commit: https://github.com/PujithaRajarapu/trustvault/commit/36c01e0

## Instructions I reused with the AI
- "One command at a time" (after pasted multi-line commands ran together).
- "Explain it in simple words" and "give me only one step".
- "Check against my real files before changing anything."
- "Do not ship edits I have not read and tested."