# Haryana CMO Grievance Portal MVP

Product-spec-driven prototype for the Haryana CMO grievance portal.

## Modules
- Citizen filing and tracking interface
- Officer work queue and CMO dashboard views
- FastAPI grievance endpoints and SLA escalation prototype
- Docker Compose development stack

## Run locally
Requirements: Docker Desktop.

```bash
docker compose up --build
```

Review `docker-compose.yml` for the exposed ports and service settings.

## Limitations and production safety
This is a development MVP, not an officially authorized government service. Do not enter real citizen personal data. Before any public production use, implement and independently test production-grade authentication/RBAC, database migrations and backups, file malware scanning, immutable audit logs, rate limiting, encrypted India-hosted storage, jurisdiction enforcement, accessibility review, disaster recovery, and authorized integrations. Aadhaar e-KYC, Family ID, OTP/SMS/email providers are not live in this prototype.

## Specification alignment
The source specification defines a Hindi-first citizen PWA, officer console, automated L1/L2/L3 escalation, dashboards, notification adapters and security requirements. This repo implements only an initial MVP subset; the README and source code must not be interpreted as evidence of government approval or production compliance.
