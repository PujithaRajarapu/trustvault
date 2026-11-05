# TrustVault

A secure document-sharing website. A document can only be opened by its owner and by people the owner has given access to. Every access, including refused ones, is written to a tamper-evident log.

**Live site:** https://trustvault-pooja.onrender.com
(The free plan sleeps when idle. The first load can take about a minute.)

## Demo logins

| Username | Role | What to try |
|---|---|---|
| demo_admin | Administrator | Open /activity/ to see the audit log and its check |
| demo_owner | Owner | Owns "Sample report". Can share and revoke |
| demo_viewer | Viewer | Has read access to the sample. Can download it but not share it |
| demo_stranger | Viewer | Has no access. Search and download are refused |

The password is given in the submission form.

## How access is decided

- One function, `authorise()` in `vault/permissions.py`, decides every access.
- If the answer is no, it writes the refusal in the audit log and shows a 404.
- Access is looked up in the database on every request, so revoking works at once.
- Only the owner can share or revoke.

## Other protections

- Files are stored outside any public path under random names.
- Uploads are checked by their content, with a size limit.
- The audit log is hash-chained, so a changed line is detected.
- Search only shows documents the user owns or was given.
- The admin activity page is for administrators only.

## Run it on your computer

    pip install -r requirements.txt
    python manage.py migrate
    python manage.py runserver

## Run the tests

    python manage.py test

## Threats

See THREATS.md.

## Known limits

- The free host deletes uploaded files when the site restarts. The database stays. The sample document is recreated on every deploy.
- Delete is not finished.

## AI use

See PROMPTS.md.