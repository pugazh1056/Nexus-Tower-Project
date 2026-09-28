# Nexus Tower: Security Architecture & RBAC Policy Guide

## 1. Overview

Nexus Tower is architected with a defense-in-depth security model to safeguard enterprise supply chain data, enforce strict role boundaries, and prevent unauthorized actions or credential leakage.

---

## 2. Authentication & Session Management

### 2.1 Credential Verification
- Authentications are performed via `POST /api/auth/login` with strict validation.
- Blank payloads, missing emails, or incorrect credentials result in immediate HTTP `400` or `401 Unauthorized` responses.
- Passwords are never stored in client cookies, local storage, or application log files.

### 2.2 Token Lifecycle
- On successful authentication, the server generates a signed Bearer token (`nexus_jwt_<base64_identity>_sig`).
- The client stores the token in `sessionStorage` (`nexus-token`) and includes it in all subsequent requests:
  ```http
  Authorization: Bearer nexus_jwt_<base64_identity>_sig
  ```
- The gateway verifies the token structure on protected endpoints via `/api/auth/me`. Invalid or expired tokens return HTTP `401 Unauthorized`.
- Logout via `POST /api/auth/logout` revokes the local session, clears role tags, and redirects the user to `login.html`.

---

## 3. Role-Based Access Control (RBAC) Matrix

The system defines 5 distinct enterprise personas with tailored permissions and page boundaries:

| Persona | Role Key | Allowed Pages | Access Scope |
| :--- | :--- | :--- | :--- |
| **Marcus Vance** (Procurement Lead) | `procurement` | `procurement.html` | Inbound purchase orders, supplier scorecards, vendor contracts, new PO creation. Unauthorized navigation redirected to Procurement console. |
| **Sarah Chen** (Inventory Lead) | `inventory` | `inventory.html` | Real-time warehouse balances, safety stock alerts, shelf-life monitoring, inventory events. |
| **Karel Novak** (Production Lead) | `production` | `production.html` | Shop floor work orders, Bill of Materials (BOM) material explosion, line throughput, downtime risks. |
| **Elena Morales** (Logistics Lead) | `logistics` | `logistics.html` | Inbound transport manifests, carrier tracking, IoT cold-chain temperature telemetry, excursion triage. |
| **David Rossi** (Operations Director) | `admin` | `control-tower.html` + All domain consoles | Full cross-domain visibility, Master Orchestrator execution, Bullwhip Effect simulation, recommendation approvals. |

### 3.1 Pre-Configured Demo Credentials (DEMO ONLY - MUST BE REPLACED BEFORE PRODUCTION)

> [!WARNING]
> **CRITICAL SECURITY NOTICE**: The following pre-configured credentials are for demonstration and presentation environments only. Do NOT deploy these credentials to a live, internet-facing production workspace without replacing them with a secure enterprise identity provider (e.g., Okta, Active Directory) or real cryptographically hashed credentials.

| Work Identity | Mapped Role | Demo Password | Default Landing Page | Mapped Profile Email |
| :--- | :--- | :--- | :--- | :--- |
| `procurement` | `procurement` | `123456` | `procurement.html` | `m.vance@nexustower.internal` |
| `inventory` | `inventory` | `123456` | `inventory.html` | `s.chen@nexustower.internal` |
| `production` | `production` | `123456` | `production.html` | `k.novak@nexustower.internal` |
| `logistics` | `logistics` | `123456` | `logistics.html` | `d.morales@nexustower.internal` |
| `admin` | `admin` | `123456` | `control-tower.html` | `ops-admin@nexustower.internal` |

---

## 4. Route Guarding & Client-Side Enforcement

The frontend controller (`assets/app.js`) implements proactive route gating on initialization:
1. Verifies if an active token and role are stored in `sessionStorage`.
2. Inspects the current page URL.
3. If a domain specialist attempts to navigate to an unauthorized console (e.g. Procurement user navigating to `logistics.html`), the guard intercepts the event and redirects the browser back to their authorized home console.
4. Non-admin users have navigational links to other domains hidden in the sidebar navigation to prevent accidental drift.

---

## 5. Supabase & Database Security

- **Server-Side Encapsulation**: The Supabase client is initialized exclusively on the server in `api_router.ts` using `process.env.SUPABASE_URL` and `process.env.SUPABASE_SECRET_KEY`.
- **Zero Frontend Leaks**: No Supabase URL, anonymous key, or service-role key is ever rendered in HTML, served in JavaScript bundles, or stored in browser storage.
- **SQL Injection Prevention**: All queries utilize parameterized builder methods provided by the Supabase SDK (`.from('table').select().eq(...)`).
- **Sanitized Errors**: Database errors returned to the client are stripped of internal connection strings and database credentials, returning generic detail messages (`{ "detail": "..." }`).

---

## 6. Input Validation & API Hardening

- **Payload Sanitization**: All POST and PATCH bodies are validated for required fields prior to database operations.
- **Strict Error Codes**:
  - `400 Bad Request` for missing required parameters.
  - `401 Unauthorized` for missing/invalid bearer tokens.
  - `404 Not Found` for non-existent entities.
  - `503 Service Unavailable` when the persistent database cannot be reached.
