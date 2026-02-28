from urllib.parse import urlparse


def normalize_domain(url: str | None) -> str | None:
    if not url:
        return None

    parsed = urlparse(url)
    domain = parsed.netloc.lower()

    if domain.startswith("www."):
        domain = domain.replace("www.", "")

    return domain