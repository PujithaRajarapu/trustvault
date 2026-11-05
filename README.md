# TrustVault

A secure document-sharing website. A document can only be opened by its owner and by people the owner has given access to. Every access, including refused ones, is written to a tamper-evident log.

**Live site:** https://trustvault-pooja.onrender.com
(The free plan sleeps when idle. The first load can take about a minute.)



## Demo Video

Watch the TrustVault project demonstration:

[Click here to watch the demo](https://youtu.be/Jk8fNHg4PpQ)


## Demo logins

All four accounts use the password `Rise@123` (demo accounts only).

| Username | Role | What to try |
|---|---|---|
| demo_admin | Administrator | Open /activity/ to see the audit log and its check |
| demo_owner | Owner | Owns the sample document. Can share, revoke and delete |
| demo_viewer | Viewer | Has read access to the sample. Can download it but not share or delete it |
| demo_stranger | Viewer | Has no access. Download is refused with a 404 |

## What I built, in short

- Register, log in, log out.
- Upload files (checked by content, 5 MB limit, cleaned filenames).
- "My documents" and "Shared with me" lists.
- Download, share (Read or Edit), revoke, and delete (owner only).
- Search that only returns documents the user owns or was given.
- A hash-chained audit log of uploads, downloads, grants, revokes, deletes and refused attempts.
- An administrator page at /activity/ that shows the log and checks that it has not been changed.
- Automated tests, including tests that one user cannot reach another user's documents.

## How access is decided (my permission model)

I chose **per-document grants**. Each document has one owner. The owner can give another person Read or Edit. A grant is one row in the database: this person, this document, this level. No row means no access.

- One function, `authorise()` in `vault/permissions.py`, decides every access.
- If the answer is no, it writes the refusal in the audit log and shows a 404, so a stranger cannot tell whether a document exists.
- Access is looked up in the database on every request, so revoking works at once.
- Read allows view and download. Edit also allows edit. Share, revoke and delete are not listed for any grant, so only the owner can do them.
- Deleted documents are refused for everyone, including the owner.
- The Administrator role is used for the /activity/ page. Administrators do not get access to other people's documents.

I did not choose folders or groups, because a smaller model that I can explain and test is safer than a bigger one with a hole in it.

## Who may call each address

| Address | Method | Who may use it |
|---|---|---|
| / | GET | Any logged-in user (own documents and shared with me) |
| /register/ | GET, POST | Anyone |
| /accounts/login/ and /accounts/logout/ | GET, POST | Anyone |
| /upload/ | GET, POST | Any logged-in user |
| /download/<id>/ | GET | The owner, or someone with a Read or Edit grant |
| /share/<id>/ | GET, POST | The owner only |
| /revoke/<id>/<user_id>/ | POST | The owner only |
| /delete/<id>/ | POST | The owner only |
| /search/ | GET | Any logged-in user (only documents they may see) |
| /activity/ | GET | Administrators only (others get 404 and the attempt is logged) |
| /admin/ | | Django's built-in admin, for superusers only. The audit log is not registered there |

## Database

Main tables (see `vault/models.py` and `vault/migrations/`):

| Table | What it holds |
|---|---|
| Profile | Which role a user has (admin, owner, viewer) |
| Document | Owner, title, category, stored file, original name, content type, size, deleted flag |
| Grant | Document, user, level (read or edit), who granted it |
| AuditLog | Time, actor, action, document, allowed or refused, detail, previous hash, own hash |

Locally it uses SQLite. On Render it uses Postgres (Neon).

## Run it on your computer (Windows PowerShell)

    git clone https://github.com/PujithaRajarapu/trustvault.git
    cd trustvault
    python -m venv .venv
    .venv\Scripts\activate
    pip install -r requirements.txt
    python manage.py migrate
    | `DEMO_PASSWORD` | The password for the demo accounts (`Rise@123`) |
    python manage.py seed_demo
    python manage.py runserver

Then open http://127.0.0.1:8000/ and log in with the demo accounts above.

On Mac or Linux, activate with `source .venv/bin/activate`.

## Run the tests

    python manage.py test

## Deploy (Render and Neon)

1. Create a free Postgres database on Neon and copy its connection string.
2. Create a Render web service from this GitHub repository.
3. Build command: `./build.sh`. Start command: `gunicorn config.wsgi`.
4. Set these environment variables on Render (they are read in `config/settings.py`):

   | Name | Value |
   |---|---|
   | `SECRET_KEY` | A long random string that is not in the repository |
   | `DEBUG` | `False` |
   | `ALLOWED_HOSTS` | Your Render host name, e.g. `trustvault-pooja.onrender.com` |
   | `CSRF_TRUSTED_ORIGINS` | `https://trustvault-pooja.onrender.com` |
   | `DATABASE_URL` | The Neon connection string |
    | `DEMO_PASSWORD` | The password for the demo accounts (`Rise@123`) |

   If `DATABASE_URL` is not set, the site uses SQLite (local development).
5. The build script installs the packages and runs the migrations. Demo accounts are created by `python manage.py seed_demo`, which needs the `DEMO_PASSWORD` variable.

## Threats

See THREATS.md.

## AI use
See PROMPTS.md. I used Claude (claude.ai) in chat to guide me step by step. I also used ChatGPT and DeepSeek after building, to test and review my code. The AI made mistakes that I caught and fixed. They are described there.

## Known limits (what is unfinished)

- The free host deletes uploaded files when the site restarts. The database stays. The sample document is recreated on every deploy. A real fix is cloud storage such as S3.
- Delete is a soft delete: the document is hidden from everyone, but the record and file stay on the server. There is no recovery page.
- Edit or rename of a document is not built.
- Attempts by people who are not logged in are not written to the audit log, because the login redirect happens first.
- The audit chain has no secret key, so someone with full database access could rewrite it, and deleting the last lines would not be noticed.
- Opening the share page is logged as an allowed "share" action even when nothing is changed.
- The pages have only simple styling (colours and spacing), so the design is basic.
- I have not tested very large files or many users at once.