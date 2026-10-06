from datetime import datetime, timedelta
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession
from .db import get_db
from .models import Workspace, Site, Keyword, RankMeasurement, CWVMeasurement, GSCMeasurement
from .schemas import SiteCreate, KeywordCreate
from .services.verification import new_token, verify_meta, verify_dns
from .services.psi import fetch_psi, extract_lighthouse, extract_crux
from .services.audit import crawl_site

app = FastAPI(title="Internal SEO Monitoring API", version="1.0.0")
app.add_middleware(CORSMiddleware, allow_origins=["http://localhost:3000"], allow_credentials=True,
                   allow_methods=["*"], allow_headers=["*"])

@app.get("/health")
async def health(): return {"status":"ok"}

@app.post("/api/v1/sites")
async def create_site(body: SiteCreate, db: AsyncSession = Depends(get_db)):
    site = Site(workspace_id=body.workspace_id, name=body.name, url=str(body.url).rstrip("/"),
                verification_type="meta", verification_token=new_token())
    db.add(site); await db.commit(); await db.refresh(site)
    return {"id":site.id,"name":site.name,"url":site.url,"verification_type":site.verification_type,
            "verification_token":site.verification_token}

@app.post("/api/v1/sites/{site_id}/verify")
async def verify_site(site_id:int, method:str="meta", db:AsyncSession=Depends(get_db)):
    site = await db.get(Site, site_id)
    if not site: raise HTTPException(404,"Site not found")
    ok = await verify_meta(site.url, site.verification_token) if method=="meta" else verify_dns(
        __import__("urllib.parse").parse.urlparse(site.url).netloc, site.verification_token)
    if not ok: raise HTTPException(400, "Verification failed")
    site.verified_at=datetime.utcnow(); await db.commit()
    return {"verified":True,"verified_at":site.verified_at}

@app.get("/api/v1/sites")
async def sites(db:AsyncSession=Depends(get_db)):
    return (await db.scalars(select(Site).order_by(desc(Site.id)))).all()

@app.post("/api/v1/keywords")
async def add_keyword(body:KeywordCreate, db:AsyncSession=Depends(get_db)):
    k=Keyword(site_id=body.site_id,keyword=body.keyword,target_url=str(body.target_url) if body.target_url else None,
              country=body.country.upper(),device=body.device)
    db.add(k); await db.commit(); await db.refresh(k); return k

@app.get("/api/v1/sites/{site_id}/dashboard")
async def dashboard(site_id:int, db:AsyncSession=Depends(get_db)):
    site=await db.get(Site,site_id)
    if not site: raise HTTPException(404,"Site not found")
    rank=(await db.scalars(select(RankMeasurement).join(Keyword).where(Keyword.site_id==site_id).order_by(desc(RankMeasurement.observed_at)).limit(20))).all()
    cwv=(await db.scalars(select(CWVMeasurement).where(CWVMeasurement.site_id==site_id).order_by(desc(CWVMeasurement.observed_at)).limit(10))).all()
    gsc=(await db.scalars(select(GSCMeasurement).where(GSCMeasurement.site_id==site_id).order_by(desc(GSCMeasurement.observed_at)).limit(10))).all()
    def row(x): return {c:getattr(x,c) for c in x.__table__.columns.keys()}
    return {"site":{"id":site.id,"name":site.name,"url":site.url,"verified_at":site.verified_at},
            "rank": [row(x) for x in rank], "cwv":[row(x) for x in cwv], "gsc":[row(x) for x in gsc]}

@app.post("/api/v1/sites/{site_id}/psi")
async def run_psi(site_id:int, db:AsyncSession=Depends(get_db)):
    site=await db.get(Site,site_id)
    if not site: raise HTTPException(404,"Site not found")
    try:
        payload=await fetch_psi(site.url,"mobile")
        lh=extract_lighthouse(payload); crux=extract_crux(payload); now=datetime.utcnow()
        db.add(CWVMeasurement(site_id=site_id,observed_at=now,strategy="mobile",source="PageSpeed Insights Lighthouse",
                              status="success",**lh))
        db.add(CWVMeasurement(site_id=site_id,observed_at=now,strategy="mobile",source="PageSpeed Insights CrUX",
                              status="success" if any(v is not None for v in crux.values()) else "data_unavailable",**crux))
        await db.commit()
        return {"lighthouse":lh,"crux":crux,"observed_at":now,"source":"PageSpeed Insights"}
    except Exception as e:
        return {"status":"data_unavailable","source":"PageSpeed Insights","last_successful_at":None,"error":str(e)}

@app.post("/api/v1/sites/{site_id}/audit")
async def run_audit(site_id:int, db:AsyncSession=Depends(get_db)):
    site=await db.get(Site,site_id)
    if not site: raise HTTPException(404,"Site not found")
    pages=await crawl_site(site.url)
    return {"status":"success","source":"self_built_crawler","page_count":len(pages),"pages":pages}

@app.get("/api/v1/sites/{site_id}/links")
async def links(site_id:int, db:AsyncSession=Depends(get_db)):
    return {"status":"data_unavailable","source":"Google Search Console Links report",
            "last_successful_at":None,
            "value":None,
            "error":"The Google Search Console API does not expose the complete Links UI report as a generic backlink-count endpoint. No broader backlink estimate is provided."}
