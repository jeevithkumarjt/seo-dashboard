from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from datetime import date

SCOPES = ["https://www.googleapis.com/auth/webmasters.readonly"]

def search_analytics(access_token: str, site_url: str, start_date: date, end_date: date):
    creds = Credentials(token=access_token, scopes=SCOPES)
    service = build("searchconsole", "v1", credentials=creds, cache_discovery=False)
    return service.searchanalytics().query(
        siteUrl=site_url,
        body={
            "startDate": start_date.isoformat(),
            "endDate": end_date.isoformat(),
            "dimensions": ["date"],
            "rowLimit": 25000
        }
    ).execute()

def links(access_token: str, site_url: str):
    creds = Credentials(token=access_token, scopes=SCOPES)
    service = build("searchconsole", "v1", credentials=creds, cache_discovery=False)
    # The Search Console API does not expose a generic "Links report" endpoint
    # equivalent to the UI's complete export. Keep this route explicit rather than
    # inventing a backlink count. Property-level link data should be imported from
    # an official Search Console export when available.
    return {"status": "data_unavailable", "source": "google_search_console_links_report",
            "error": "Google Search Console API does not expose the complete Links UI report as a count endpoint."}
