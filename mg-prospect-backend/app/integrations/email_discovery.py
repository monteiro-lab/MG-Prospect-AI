"""
Email Discovery Module
Scrapes business websites to find contact email addresses.
Used as an enrichment step during campaign execution, since the
Google Places API does not return email addresses.
"""

import re
import httpx
from typing import Optional, List
from urllib.parse import urljoin, urlparse


# Paths commonly used for contact pages on Brazilian business websites
CONTACT_PATHS = [
    "/contato",
    "/contatos",
    "/contact",
    "/fale-conosco",
    "/sobre",
    "/about",
    "/quem-somos",
]

# Domains that should never be returned as lead emails
BLACKLISTED_DOMAINS = {
    "example.com",
    "sentry.io",
    "wixpress.com",
    "wordpress.com",
    "w3.org",
    "schema.org",
    "googleapis.com",
    "google.com",
    "facebook.com",
    "twitter.com",
    "instagram.com",
    "linkedin.com",
    "youtube.com",
    "cloudflare.com",
    "jquery.com",
    "gravatar.com",
    "wp.com",
    "bootstrapcdn.com",
    "gstatic.com",
    "googletagmanager.com",
    "google-analytics.com",
}

# Email prefixes that indicate a commercial or contact address (higher priority)
PRIORITY_PREFIXES = [
    "contato",
    "comercial",
    "atendimento",
    "vendas",
    "financeiro",
    "administrativo",
    "sac",
    "suporte",
    "faleconosco",
    "contabilidade",
    "info",
    "adm",
]

# Regex pattern for email extraction
EMAIL_PATTERN = re.compile(
    r"[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}",
    re.IGNORECASE,
)


def _is_valid_email(email: str) -> bool:
    """Filter out emails that are clearly not business contacts."""
    email = email.lower().strip()

    # Must have at least one dot in the domain part
    parts = email.split("@")
    if len(parts) != 2:
        return False

    local, domain = parts

    # Block blacklisted domains
    if domain in BLACKLISTED_DOMAINS:
        return False

    # Block image/file extensions that regex might catch
    if domain.endswith((".png", ".jpg", ".jpeg", ".gif", ".svg", ".webp", ".css", ".js")):
        return False

    # Block very short local parts (likely false positives)
    if len(local) < 2:
        return False

    # Block emails with obvious template variables
    if "{" in email or "}" in email or "%" in email:
        return False

    return True


def _score_email(email: str) -> int:
    """
    Score an email to determine how likely it is to be a commercial contact.
    Higher score = better candidate.
    """
    email_lower = email.lower()
    local_part = email_lower.split("@")[0]

    score = 0

    # Boost for known commercial prefixes
    for prefix in PRIORITY_PREFIXES:
        if local_part.startswith(prefix):
            score += 10
            break

    # Slight penalty for generic/personal-looking addresses
    if local_part.startswith("noreply") or local_part.startswith("no-reply"):
        score -= 20
    if local_part.startswith("newsletter"):
        score -= 15
    if local_part.startswith("dev") or local_part.startswith("test"):
        score -= 15
    if local_part.startswith("webmaster"):
        score -= 5

    # Prefer shorter local parts (usually more "official")
    if len(local_part) <= 15:
        score += 2

    return score


async def _fetch_page(client: httpx.AsyncClient, url: str) -> Optional[str]:
    """Fetch a single page and return its HTML content, or None on failure."""
    try:
        response = await client.get(
            url,
            follow_redirects=True,
            timeout=10.0,
        )
        if response.status_code == 200:
            content_type = response.headers.get("content-type", "")
            if "text/html" in content_type or "text/plain" in content_type:
                return response.text
    except Exception:
        pass
    return None


def _extract_emails_from_html(html: str) -> List[str]:
    """Extract all email-like strings from raw HTML."""
    raw_matches = EMAIL_PATTERN.findall(html)
    return [e for e in set(raw_matches) if _is_valid_email(e)]


async def discover_email(website_url: str) -> Optional[str]:
    """
    Given a business website URL, attempt to find the best contact email.

    Strategy:
    1. Fetch the homepage.
    2. Fetch common contact page paths.
    3. Collect all emails found across all pages.
    4. Score and rank them.
    5. Return the best candidate, or None.
    """
    if not website_url:
        return None

    # Normalize the base URL
    parsed = urlparse(website_url)
    if not parsed.scheme:
        website_url = f"https://{website_url}"
        parsed = urlparse(website_url)

    base_url = f"{parsed.scheme}://{parsed.netloc}"

    all_emails: List[str] = []

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                       "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "pt-BR,pt;q=0.9,en;q=0.8",
    }

    async with httpx.AsyncClient(headers=headers, verify=False) as client:
        # 1. Fetch the homepage
        homepage_html = await _fetch_page(client, website_url)
        if homepage_html:
            all_emails.extend(_extract_emails_from_html(homepage_html))

        # 2. Fetch contact-related subpages
        for path in CONTACT_PATHS:
            page_url = urljoin(base_url, path)
            html = await _fetch_page(client, page_url)
            if html:
                found = _extract_emails_from_html(html)
                all_emails.extend(found)

    if not all_emails:
        return None

    # Deduplicate
    unique_emails = list(set(e.lower() for e in all_emails))

    # Score and sort (highest score first)
    scored = sorted(unique_emails, key=lambda e: _score_email(e), reverse=True)

    return scored[0]
