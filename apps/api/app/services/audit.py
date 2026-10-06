import asyncio, re
from collections import Counter
from urllib.parse import urljoin, urlparse
import httpx
from bs4 import BeautifulSoup

async def crawl_site(start_url: str, max_pages: int = 100):
    parsed = urlparse(start_url)
    host = parsed.netloc
    queue = [start_url]
    seen = set()
    pages = []
    async with httpx.AsyncClient(follow_redirects=True, timeout=20) as client:
        while queue and len(pages) < max_pages:
            url = queue.pop(0)
            if url in seen or urlparse(url).netloc != host:
                continue
            seen.add(url)
            try:
                r = await client.get(url, headers={"User-Agent":"InternalSEOAuditBot/1.0"})
                soup = BeautifulSoup(r.text, "lxml") if "text/html" in r.headers.get("content-type","") else None
                if not soup:
                    pages.append({"url":url,"status_code":r.status_code})
                    continue
                links = [urljoin(url,a.get("href")) for a in soup.find_all("a", href=True)]
                internal = [x for x in links if urlparse(x).netloc == host and urlparse(x).scheme in ("http","https")]
                queue.extend(x.split("#")[0] for x in internal if x.split("#")[0] not in seen)
                imgs = soup.find_all("img")
                titles = [x.get_text(" ", strip=True) for x in soup.find_all("title")]
                metas = [x.get("content") for x in soup.find_all("meta", attrs={"name": re.compile("^description$", re.I)})]
                h1 = soup.find_all("h1")
                canonical = soup.find("link", rel=lambda v: v and "canonical" in v)
                headings = [h.name for h in soup.find_all(re.compile("^h[1-6]$"))]
                pages.append({
                    "url":str(r.url), "status_code":r.status_code,
                    "title": titles[0] if titles else None,
                    "meta_description": metas[0] if metas else None,
                    "h1_count":len(h1),
                    "heading_errors": (["missing_h1"] if not h1 else []) + (["multiple_h1"] if len(h1)>1 else []),
                    "missing_alt_count":sum(1 for i in imgs if not (i.get("alt") or "").strip()),
                    "canonical": canonical.get("href") if canonical else None,
                    "canonical_valid": bool(canonical and canonical.get("href")),
                    "headings": headings,
                    "broken_links": None,
                    "redirect_chain": [],
                    "schema_errors": [],
                    "content_hash": hash(soup.get_text(" ", strip=True))
                })
            except Exception as e:
                pages.append({"url":url,"status_code":None,"error":str(e)})
            await asyncio.sleep(0.5)
    title_counts = Counter(p.get("title") for p in pages if p.get("title"))
    content_counts = Counter(p.get("content_hash") for p in pages if p.get("content_hash") is not None)
    for p in pages:
        p["duplicate_title"] = bool(p.get("title") and title_counts[p["title"]] > 1)
        p["duplicate_content"] = bool(p.get("content_hash") is not None and content_counts[p["content_hash"]] > 1)
        p.pop("content_hash", None)
    return pages
