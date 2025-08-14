# Security Policy (Public Summary) — DUMMY

**Scope:** Public summary for grant reviewers & Infosec.  
This contains NO real credentials, NO real endpoints, and NO infrastructure secrets.

## Data Handling
- No PII stored. Requests are processed in-memory only.
- Logs are aggregate-only, with no wallet addresses, IPs, or personal identifiers.
- Example aggregate fields: `date`, `total_requests`, `unique_clients_hashed_rotating`, `chains_touched`, `high_risk_flags`.

## Credentials & Secrets
- Stored in environment variables (never in code or repository).
- Rotated regularly (e.g., every 30–60 days) or immediately if exposure is suspected.
- Access is restricted based on least-privilege principle.

## Application & Network Security
- TLS enforced for all communications.
- Generic security headers targeted: HSTS, CSP, X-Frame-Options, Referrer-Policy.
- CORS restricted to approved domains (not disclosed here).

## Dependencies & Builds
- Dependencies audited regularly; critical/high issues patched before release.
- Secret scanning performed prior to deployments.

## Incident Response (Public Outline)
- Detect → Contain → Eradicate → Recover → Postmortem.
- External security contact: security@example.com (dummy address).
- Vulnerability disclosure via responsible channels; no real data should be sent.
