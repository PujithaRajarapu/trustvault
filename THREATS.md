# THREATS.md

For each threat: how it could be attacked, what I did, and which test covers it.

| # | Threat | What I did | Test |
|---|--------|-----------|------|
| 1 | A stranger opens or downloads someone else's document by typing its URL | Every document page calls the one function `authorise()` before doing anything | test_stranger_gets_404 |
| 2 | Someone guesses document numbers to find documents | A refused request and a missing document both give the same 404, so nothing is revealed | test_missing_document_gives_404 |
| 3 | A user keeps access after the owner revokes it | Access is looked up in the database on every request. No tokens or links that outlive a revoke | test_grant_allows_then_revoke_blocks |
| 4 | A person with only Read or Edit access shares the document | Share and revoke are owner-only inside `authorise()` | test_read_grant_cannot_share, test_edit_grant_cannot_share |
| 5 | A stranger gives themselves access or removes someone else's access | Share and revoke go through `authorise()` | test_stranger_cannot_grant_themselves_access, test_stranger_cannot_revoke_someone_elses_grant |
| 6 | Another website tricks a logged-in owner into revoking or deleting (CSRF) | Revoke and delete only work with POST and a CSRF token. Delete refuses GET | Delete needs POST: `vault/test_delete.py`. The CSRF token itself is not tested |
| 7 | A deleted document is still opened | Deleted documents are treated as missing, even for the owner | test_deleted_document_is_refused_even_for_owner |
| 8 | Someone edits the audit log to hide what they did | Each entry stores the hash of the one before it. `verify_chain()` finds any change. The log is not in Django admin | test_audit_chain_detects_tampering |
| 9 | Refused attempts leave no trace | Refusals are written to the audit log too | test_refusal_is_logged |
| 10 | A normal user reads the admin activity page | The page is for administrators only. Everyone else gets 404, and the attempt is logged | Checked by hand, test not written yet |
| 11 | A harmful file is uploaded with a fake extension | The file type is decided from the file's bytes, not its name. Size is limited to 5 MB | Not tested yet |
| 12 | A file name like ../../x writes outside the folder | Files are saved under a random name. The user's name is only for display | Not tested yet |
| 13 | Files are reached by a public or guessable URL | Files live in `private_files`, which has no public URL. They are only sent by the download page | Not tested yet |
| 14 | A stranger, or someone with only Read or Edit access, deletes a document | Delete goes through `authorise()` and is owner-only. It needs POST | `vault/test_delete.py` (stranger, read grant, edit grant, GET, anonymous, refusal logged) |
| 15 | Search shows documents the user may not see | Search only looks at documents the user owns or has a grant for | test_stranger_does_not_find_it, test_owner_finds_own_document |
| 16 | A person who is not logged in reaches a page | Pages use `@login_required` and redirect to the login page | test_anonymous_is_sent_to_login (download page only) |
| 17 | Debug pages leak code and settings | Production sets `DEBUG=False` on Render. Cookies become secure only then. The code defaults to debug ON if the variable is missing, which is a risk | Checked by hand on the live site |
| 18 | The secret key is public | The fallback key in `settings.py` is only for local use. The live site uses its own `SECRET_KEY` from the environment | Not tested |
| 19 | Someone guesses the Django `/admin/` login | Only superusers can enter. The audit log is not registered there. The address is still public | Not tested yet |
| 20 | Someone logs in with the demo passwords | The demo password is public on purpose for judges. The demo accounts hold only sample data. Real data must never be put on this site | Not applicable |

## Not finished (honest list)
- Free hosting deletes uploaded files when the site restarts. The database rows stay. The real fix is cloud storage such as S3.
- Delete is a soft delete. The record and file stay on the server.
- Attempts by people who are not logged in are not written to the audit log, because the login redirect happens first.
- The audit chain has no secret key. Someone with full database access could rebuild the whole chain, and deleting the last entries would not be noticed.
- Two requests at the same instant could both read the same "last" log entry and break the chain. I have not tested this.
- Opening the share page is logged as an allowed "share" action even when nothing is changed.
- There is no rate limit on login, so passwords can be guessed.
- I have not tested very large files or many users at once.