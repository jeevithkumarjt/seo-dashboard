import asyncio, os
from datetime import datetime
from urllib.parse import quote_plus
from playwright.async_api import async_playwright
from .celery_app import celery

@celery.task(bind=True, autoretry_for=(Exception,), retry_backoff=True, max_retries=2)
def scrape_rank(self, keyword: str, target_domain: str, country: str="US", device: str="desktop"):
    return asyncio.run(_scrape(keyword,target_domain,country,device))

async def _scrape(keyword,target_domain,country,device):
    async with async_playwright() as p:
        browser=await p.chromium.launch(headless=True)
        context=await browser.new_context(
            user_agent="Mozilla/5.0 (compatible; InternalSEOResearch/1.0)",
            viewport={"width":1280,"height":900},
            locale=f"en-{country.upper()}"
        )
        page=await context.new_page()
        try:
            url="https://www.google.com/search?q="+quote_plus(keyword)+"&num=100"
            response=await page.goto(url,wait_until="domcontentloaded",timeout=30000)
            html=(await page.content()).lower()
            if any(x in html for x in ("unusual traffic","captcha","verify you are a human","recaptcha")):
                return {"status":"captcha","rank":None,"found_url":None,"source":"self_built_serp_scraper",
                        "observed_at":datetime.utcnow().isoformat()}
            if response and response.status >= 400:
                return {"status":"blocked","rank":None,"found_url":None,"source":"self_built_serp_scraper",
                        "observed_at":datetime.utcnow().isoformat()}
            links=await page.locator("a").evaluate_all("""els => els.map(a => ({href:a.href,text:a.innerText})).filter(x=>x.href)""")
            rank=0
            found=None
            for x in links:
                href=x["href"]
                if target_domain.lower() in href.lower() and "google." not in href.lower():
                    rank += 1
                    if found is None: found=href
                if rank >= 100: break
            return {"status":"success" if found else "not_found_in_top_100","rank":rank or None,
                    "found_url":found,"source":"self_built_serp_scraper","observed_at":datetime.utcnow().isoformat()}
        except Exception as e:
            return {"status":"unavailable","rank":None,"found_url":None,"source":"self_built_serp_scraper",
                    "error":str(e),"observed_at":datetime.utcnow().isoformat()}
        finally:
            await browser.close()

@celery.task
def schedule_site_audit(site_id:int):
    return {"status":"queued","site_id":site_id}
