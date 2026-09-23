import hashlib
from urllib.parse import urlsplit, urlunsplit


def normalize_url(url: str) -> str:
    value = url.strip()

    if "://" not in value:
        value = f"http://{value}"

    parsed = urlsplit(value)

    scheme = parsed.scheme.lower()
    hostname = (parsed.hostname or "").lower()

    if not hostname:
        raise ValueError("URL must include a hostname.")

    port = parsed.port

    if (scheme == "http" and port == 80) or (scheme == "https" and port == 443):
        netloc = hostname
    elif port:
        netloc = f"{hostname}:{port}"
    else:
        netloc = hostname

    path = parsed.path or "/"

    return urlunsplit((scheme, netloc, path, parsed.query, ""))


def create_lookup_key(normalized_url: str) -> str:
    return hashlib.sha256(normalized_url.encode("utf-8")).hexdigest()