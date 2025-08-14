# Data Flow (Public Diagram) — DUMMY

**Purpose:** Show stateless processing without exposing real architecture.

Client
|
|  (HTTPS/TLS)
v
[Request Gateway] –(CORS allowlist)–>
|
v
[Validation Engine - in-memory only]
|  - Fetches public blockchain data from generic providers (names omitted)
|  - Applies heuristic + AI scoring (details abstracted)
|  - No database writes of request payloads or wallet addresses
|
v
[JSON Response Builder]
|
v
Client receives risk score + non-sensitive metadata

**Aggregate-only Logging (dummy fields):**
- `date`
- `total_requests`
- `unique_clients_hashed_rotating`
- `chains_touched`
- `high_risk_flags`

**Controls (generic):**
- TLS enforced
- Security headers enabled (HSTS, CSP, X-Frame-Options, Referrer-Policy)
- Rate limiting + WAF
- No persistence of user-submitted data
