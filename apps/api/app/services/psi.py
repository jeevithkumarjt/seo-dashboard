from datetime import datetime
import httpx
from ..config import settings

PSI = "https://www.googleapis.com/pagespeedonline/v5/runPagespeed"

async def fetch_psi(url: str, strategy: str):
    params = {"url": url, "strategy": strategy, "category": "performance"}
    if settings.pagespeed_api_key:
        params["key"] = settings.pagespeed_api_key
    async with httpx.AsyncClient(timeout=90) as client:
        r = await client.get(PSI, params=params)
        r.raise_for_status()
        return r.json()

def extract_lighthouse(payload):
    a = payload.get("lighthouseResult", {}).get("audits", {})
    def num(k):
        x = a.get(k, {}).get("numericValue")
        return float(x) if isinstance(x, (int,float)) else None
    return {
        "lcp_ms": num("largest-contentful-paint"),
        "cls": num("cumulative-layout-shift"),
        "inp_ms": num("interaction-to-next-paint"),
        "fcp_ms": num("first-contentful-paint"),
    }

def extract_crux(payload):
    # PSI exposes CrUX field distributions when available.
    loading = payload.get("loadingExperience", {})
    metrics = loading.get("metrics", {})
    def p75(name):
        v = metrics.get(name, {}).get("percentiles", {}).get("p75")
        return float(v) if isinstance(v,(int,float)) else None
    return {
        "lcp_ms": p75("LARGEST_CONTENTFUL_PAINT_MS"),
        "cls": p75("CUMULATIVE_LAYOUT_SHIFT_SCORE"),
        "inp_ms": p75("INTERACTION_TO_NEXT_PAINT"),
        "fcp_ms": p75("FIRST_CONTENTFUL_PAINT_MS"),
    }
