import secrets, socket
from datetime import datetime
import httpx
import dns.resolver

def new_token():
    return secrets.token_urlsafe(24)

async def verify_meta(url: str, token: str) -> bool:
    async with httpx.AsyncClient(follow_redirects=True, timeout=15) as client:
        r = await client.get(url, headers={"User-Agent": "InternalSEOVerifier/1.0"})
        return f'<meta name="seo-monitor-verification" content="{token}"' in r.text.lower()

def verify_dns(host: str, token: str) -> bool:
    try:
        answers = dns.resolver.resolve(f"_seo-monitor.{host}", "TXT")
        return any(token in str(v) for a in answers)
    except Exception:
        return False
