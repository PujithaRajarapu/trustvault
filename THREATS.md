# THREATS.md

For each threat: how it could be attacked, what I did, and which test covers it.

| # | Threat | What I did | Test |
|---|--------|-----------|------|
| 1 | A stranger opens or downloads someone else's document by typing its URL | Every document page calls the one function `authorise()` before doing anything | test_stranger_gets_404 |
| 2 | Someone guesses document numbers to find documents | A refused request and a missing document both give the same 404, so nothing is revealed | test_missing_document_gives_404 |
| 3 | A user keeps access after the owner revokes it | Access is looked up in the database on every request. No tokens or links that outlive a revoke | test_grant_allows_then_revoke_blocks |
| 4 | A person with only Read or Edit access shares the document | Share and revoke are owner-only inside `authorise()` | test_read_grant_cannot_share, test_edit_grant_cannot_share |
| 5 | A stranger gives themselves access or removes someone else's access | Share and revoke go through `authorise()` | test_stranger_cannot_grant_themselves_access, test_stranger_cannot_revoke_someone_elses_grant |
| 6 | Another website tricks a logged-in owner into revoking (CSRF) | Revoke only works with POST and a CSRF token | Not tested yet |
| 7 | A deleted document is still opened | Deleted documents are treated as missing, even for the owner | test_deleted_document_is_refused_even_for_owner |
| 8 | Someone edits the audit log to hide what they did | Each entry stores the hash of the one before it. `verify_chain()` finds any change | test_audit_chain_detects_tampering |
| 9 | Refused attempts leave no trace | Refusals are written to the audit log too | test_refusal_is_logged |
| 10 | A normal user reads the admin activity page | The page is for administrators only. Everyone else gets 404 | Checked by hand, test not written yet |
| 11 | A harmful file is uploaded with a fake extension | The file type is decided from the file's bytes, not its name. Size is limited | Not tested yet |
| 12 | A file name like ../../x writes outside the folder | Files are saved under a random name. The user's name is only for display | Not tested yet |
| 13 | Files are reached by a public or guessable URL | Files live in `private_files`, which has no public URL. They are only sent by the download page | Not tested yet |

## Not finished (honest list)
- Search is not built yet. When it is, it must only look at documents the user is allowed to see.
- Delete is not built yet.
- Free hosting deletes uploaded files when the site restarts. The database rows stay.
