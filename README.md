# Haryana CMO Grievance Portal

A beautiful, responsive MVP based on the supplied Haryana CMO Grievance Portal Product Specification.

## Included
- Citizen grievance filing and tracking
- Hindi/English-ready interface
- Officer workspace
- CMO command centre
- SLA escalation prototype
- FastAPI backend
- Docker Compose development stack

## Run
```bash
docker compose up --build
```

Then open http://localhost:3000 and API docs at http://localhost:8000/docs.

## Production warning
This is a development MVP, not an officially authorized Haryana Government service. Do not enter real citizen personal data. Aadhaar/Family ID, official OTP/SMS/email, production RBAC, PostGIS persistence, malware scanning, immutable audit logs, security hardening, authorized government integrations, India-hosted production infrastructure and formal security/compliance review remain required before real-world deployment.

## Source alignment
The supplied specification calls for a Hindi-first citizen PWA, officer console, L1/L2/L3 escalation, dashboards, notifications, integrations and security controls. This repository is an initial demonstrator subset and makes no claim of government approval or production compliance.
