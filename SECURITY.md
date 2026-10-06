# Security / production checklist

- Put Nginx behind HTTPS.
- Restrict dashboard access to the internal network/VPN/SSO boundary.
- Replace permissive CORS with the exact dashboard origin.
- Encrypt Google OAuth refresh tokens at rest; this scaffold deliberately does not persist tokens.
- Add per-workspace authorization before exposing the API beyond localhost.
- Add CSRF protection if cookie authentication is introduced.
- Add request limits and SSRF protection to all crawler/URL endpoints.
- Do not allow arbitrary private-IP targets from crawler inputs.
- Use a dedicated PostgreSQL role with least privilege.
- Rotate webhook/SMTP credentials.
- Never log OAuth tokens or credentials.
- Add Alembic migrations before production schema changes.
