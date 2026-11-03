import os
import re

MAX_SIZE = 5 * 1024 * 1024  # 5 MB


def sniff_type(head):
    """Decide the file type from the first bytes, not from the name."""
    if head.startswith(b"%PDF-"):
        return "application/pdf"
    if head.startswith(b"\x89PNG\r\n\x1a\n"):
        return "image/png"
    if head.startswith(b"\xff\xd8\xff"):
        return "image/jpeg"
    return None


def clean_name(name):
    """Safe name for showing on screen only. Never used on disk."""
    name = os.path.basename(name.replace("\\", "/"))
    name = re.sub(r"[^A-Za-z0-9._ -]", "_", name).strip(" .")
    return (name or "file")[:100]