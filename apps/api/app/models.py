from datetime import datetime
from sqlalchemy import String, Text, Boolean, DateTime, Float, Integer, ForeignKey, JSON, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .db import Base

class Workspace(Base):
    __tablename__ = "workspaces"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(160))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    sites = relationship("Site", back_populates="workspace")

class Site(Base):
    __tablename__ = "sites"
    id: Mapped[int] = mapped_column(primary_key=True)
    workspace_id: Mapped[int] = mapped_column(ForeignKey("workspaces.id"), index=True)
    name: Mapped[str] = mapped_column(String(160))
    url: Mapped[str] = mapped_column(String(2048), unique=True)
    verification_type: Mapped[str | None] = mapped_column(String(20))
    verification_token: Mapped[str | None] = mapped_column(String(128))
    verified_at: Mapped[datetime | None] = mapped_column(DateTime)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    workspace = relationship("Workspace", back_populates="sites")
    keywords = relationship("Keyword", back_populates="site")

class Keyword(Base):
    __tablename__ = "keywords"
    id: Mapped[int] = mapped_column(primary_key=True)
    site_id: Mapped[int] = mapped_column(ForeignKey("sites.id"), index=True)
    keyword: Mapped[str] = mapped_column(String(500))
    target_url: Mapped[str | None] = mapped_column(String(2048))
    country: Mapped[str] = mapped_column(String(2), default="US")
    device: Mapped[str] = mapped_column(String(20), default="desktop")
    active: Mapped[bool] = mapped_column(Boolean, default=True)
    site = relationship("Site", back_populates="keywords")
    __table_args__ = (UniqueConstraint("site_id", "keyword", "country", "device"),)

class RankMeasurement(Base):
    __tablename__ = "rank_measurements"
    id: Mapped[int] = mapped_column(primary_key=True)
    keyword_id: Mapped[int] = mapped_column(ForeignKey("keywords.id"), index=True)
    observed_at: Mapped[datetime] = mapped_column(DateTime, index=True)
    rank: Mapped[int | None] = mapped_column(Integer, nullable=True)
    found_url: Mapped[str | None] = mapped_column(String(2048))
    status: Mapped[str] = mapped_column(String(40)) # success / captcha / blocked / unavailable
    source: Mapped[str] = mapped_column(String(80), default="self_built_serp_scraper")
    error: Mapped[str | None] = mapped_column(Text)

class CWVMeasurement(Base):
    __tablename__ = "cwv_measurements"
    id: Mapped[int] = mapped_column(primary_key=True)
    site_id: Mapped[int] = mapped_column(ForeignKey("sites.id"), index=True)
    observed_at: Mapped[datetime] = mapped_column(DateTime, index=True)
    strategy: Mapped[str] = mapped_column(String(20))
    lcp_ms: Mapped[float | None]
    cls: Mapped[float | None]
    inp_ms: Mapped[float | None]
    fcp_ms: Mapped[float | None]
    source: Mapped[str] # PageSpeed Insights Lighthouse or CrUX
    status: Mapped[str] = mapped_column(String(40))
    error: Mapped[str | None] = mapped_column(Text)

class GSCMeasurement(Base):
    __tablename__ = "gsc_measurements"
    id: Mapped[int] = mapped_column(primary_key=True)
    site_id: Mapped[int] = mapped_column(ForeignKey("sites.id"), index=True)
    observed_at: Mapped[datetime] = mapped_column(DateTime, index=True)
    start_date: Mapped[str]
    end_date: Mapped[str]
    clicks: Mapped[float | None]
    impressions: Mapped[float | None]
    ctr: Mapped[float | None]
    position: Mapped[float | None]
    source: Mapped[str] = mapped_column(String(80), default="google_search_console")

class AuditRun(Base):
    __tablename__ = "audit_runs"
    id: Mapped[int] = mapped_column(primary_key=True)
    site_id: Mapped[int] = mapped_column(ForeignKey("sites.id"), index=True)
    started_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime)
    status: Mapped[str] = mapped_column(String(40))
    source: Mapped[str] = mapped_column(String(80), default="self_built_crawler")
    error: Mapped[str | None] = mapped_column(Text)

class PageAuditResult(Base):
    __tablename__ = "page_audit_results"
    id: Mapped[int] = mapped_column(primary_key=True)
    audit_run_id: Mapped[int] = mapped_column(ForeignKey("audit_runs.id"), index=True)
    url: Mapped[str] = mapped_column(String(2048))
    status_code: Mapped[int | None]
    title: Mapped[str | None] = mapped_column(Text)
    meta_description: Mapped[str | None] = mapped_column(Text)
    h1_count: Mapped[int | None]
    heading_errors: Mapped[list | None] = mapped_column(JSON)
    missing_alt_count: Mapped[int | None]
    canonical: Mapped[str | None] = mapped_column(String(2048))
    canonical_valid: Mapped[bool | None]
    duplicate_title: Mapped[bool | None]
    duplicate_content: Mapped[bool | None]
    broken_links: Mapped[int | None]
    redirect_chain: Mapped[list | None] = mapped_column(JSON)
    robots_allowed: Mapped[bool | None]
    sitemap_listed: Mapped[bool | None]
    schema_errors: Mapped[list | None] = mapped_column(JSON)
    source: Mapped[str] = mapped_column(String(80), default="self_built_crawler")
