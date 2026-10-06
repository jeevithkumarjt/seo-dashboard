# SEO Audit & Monitoring Dashboard

An internal dashboard that watches a website's SEO using only free, official data
sources, and refuses to show a number it cannot actually measure.

> **Status: In progress**
>
> **What works**
>
> - Docker Compose stack: Next.js, FastAPI, Celery worker, TimescaleDB, Redis
> - Site registration with meta-tag and DNS TXT ownership verification
> - A self-built crawler that walks a site and collects page-level findings:
>   titles, meta descriptions, H1 problems, missing image alt text, canonical tags,
>   heading order, duplicate titles and duplicate content
> - PageSpeed Insights pulls, with Lighthouse lab data and CrUX field data stored as
>   separate rows rather than merged into one score
> - A dashboard UI showing rank history, Core Web Vitals, Search Console and
>   backlink panels
> - Honest data states: every panel names its source and shows "data unavailable"
>   instead of a fabricated value
>
> **What's next**
>
> - The issue list with a plain-language "how to fix" for each finding
> - Persisting audit runs and page findings (the tables exist, the writes are not
>   wired up yet)
> - Google Search Console data sync
> - Scheduled rank tracking over time
> - Alerts when something regresses

Treat it as a working prototype, not a finished product.

## The problem

Most SEO tools either cost money or quietly fill gaps with estimates. When a number
is missing they substitute an average, an inference or a proprietary score you cannot
check. That is worse than useless for an internal tool, because you end up
optimising for a figure that nobody can reproduce.

This dashboard has one rule: **no fabricated values.** If a source fails or a
measurement is unavailable, the panel says so, names the source, and shows when the
last successful reading was.

## Architecture

```
   Browser
      |
      v
+------------------+       HTTP        +------------------+
| Next.js (web)    | ----------------> | FastAPI (api)    |
| localhost:3000   |                   | localhost:8000   |
+------------------+                   +---+-----------+--+
                                           |           |
                          writes/reads     |           | enqueue
                              +------------+           +-------------+
                              v                                      v
                    +--------------------+                 +--------------------+
                    | TimescaleDB        |                 | Redis              |
                    | rank / CWV / GSC   |                 | Celery broker      |
                    | time-series tables |                 +---------+----------+
                    +--------------------+                           |
                                                                     v
                                                           +--------------------+
                                                           | Celery worker      |
                                                           | Playwright SERP    |
                                                           | scraper            |
                                                           +--------------------+
```

The crawler itself runs inside the API with `httpx` and BeautifulSoup. Playwright is
used only for the Google SERP rank scraper in the worker, because that needs a real
browser.

## Tech stack

| Layer | Technology |
| --- | --- |
| API | FastAPI, SQLAlchemy (async), Pydantic settings |
| Web | Next.js (App Router), Tailwind CSS, Recharts |
| Worker | Celery, Playwright |
| Crawler | httpx, BeautifulSoup, lxml |
| Database | PostgreSQL 16 + TimescaleDB |
| Queue | Redis |
| Data sources | Google Search Console API, PageSpeed Insights API (both free) |
| Infra | Docker Compose, plus an Nginx and PM2 example in `deploy/` |

## Data policy

- No fabricated values, and no invented SEO score.
- Failed or incomplete sources return `data_unavailable` with the source name and the
  last successful timestamp.
- Google Search Console is the only source used for Google search performance.
- Backlinks come from the Search Console Links report only, and are labelled as such.
- PageSpeed lab data and CrUX field data are stored and displayed separately.
- SERP scraping is best-effort. On a CAPTCHA or a block, the rank stays null rather
  than becoming a 0 or an estimate.
- No Ahrefs, Semrush, Moz, DataForSEO, SerpApi or any other paid SEO API.

## Running it

```bash
git clone https://github.com/jeevithkumarjt/seo-dashboard.git
cd seo-dashboard

cp .env.example .env
# Every key is optional. Add only the free credentials you actually have.

docker compose up --build
```

Open http://localhost:3000.

`.env.example` lists everything. What you might want to set:

| Key | Purpose |
| --- | --- |
| `GSC_CLIENT_ID` / `GSC_CLIENT_SECRET` | Google OAuth, for Search Console |
| `PAGESPEED_API_KEY` | Optional — the PageSpeed API also works without one |
| `DISCORD_WEBHOOK_URL` / `SLACK_WEBHOOK_URL` | Optional alert destinations |

For local development without Docker:

```bash
pnpm install
pnpm dev
```

## Google Search Console

Create an OAuth consent screen and an OAuth client in Google Cloud, then enable the
Search Console API. Both are free; API usage is subject to Google's current quotas.

The callback is `/api/v1/integrations/google/callback`. For a real deployment, put
the API behind HTTPS and register the exact HTTPS callback URL.

## Screenshots

Screenshots will be added once the issue and fix view is built.

## Operational note

A self-built Google SERP scraper runs into CAPTCHAs, consent pages, rate limits and
blocks. This implementation never turns those failures into a rank of 0 or an
estimate — the measurement stays unavailable for that observation.

## Security

`SECURITY.md` is the production checklist. The short version: this is meant to run
behind a VPN or an internal network boundary, and it is not hardened for exposure to
the public internet yet.

## License

[MIT](LICENSE)
