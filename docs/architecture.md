# Nexus Tower: System Architecture & Technical Specification

## 1. Executive Summary

**Nexus Tower** is an enterprise-grade FMCG Supply Chain Operations Cockpit and Decision Intelligence Platform. It synchronizes four operational domains—**Procurement**, **Inventory**, **Production**, and **Logistics**—into a centralized **Control Tower** driven by autonomous agent orchestration, forward and backward Bullwhip Effect quantification, and automated decision recommendations.

```
┌──────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                       NEXUS TOWER PLATFORM                                       │
└──────────────────────────────────────────────────────────────────────────────────────────────────┘
                                                  │
                 ┌────────────────────────────────┴────────────────────────────────┐
                 ▼                                                                 ▼
   ┌───────────────────────────┐                                     ┌───────────────────────────┐
   │    PRESENTATION LAYER     │                                     │   NATIVE BACKEND GATEWAY  │
   │ ───────────────────────── │                                     │ ───────────────────────── │
   │ • index.html (Landing)    │                                     │ • Express 4.21.2 + TS     │
   │ • login.html (Auth/Roles) │      HTTP / JSON REST API           │ • CORS & Static Pipeline  │
   │ • control-tower.html      │ ◄─────────────────────────────────► │ • Native TypeScript Router│
   │ • procurement.html        │       (Bearer JWT Tokens)           │ • Master Orchestrator     │
   │ • inventory.html          │                                     │ • Forward/Backward Engine │
   │ • production.html         │                                     │ • Optional FastAPI Proxy  │
   │ • logistics.html          │                                     └─────────────┬─────────────┘
   └───────────────────────────┘                                                   │
                                                                                   ▼
                                                                     ┌───────────────────────────┐
                                                                     │     PERSISTENCE TIER      │
                                                                     │ ───────────────────────── │
                                                                     │ • Supabase PostgreSQL     │
                                                                     │ • Row-Level Security      │
                                                                     │ • 001_initial_schema.sql  │
                                                                     │ • 002_demo_seed_data.sql  │
                                                                     └───────────────────────────┘
```

---

## 2. Core Architectural Principles

1. **Strict Server-Side Credential Isolation**:
   No database connection strings, Supabase secret keys, or service-role credentials ever leave the server-side gateway. The browser client interacts strictly through sanitized `/api/*` endpoints.

2. **Unified API Gateway Architecture**:
   The platform runs a lightweight, high-performance Node.js / Express TypeScript gateway on port 3000 (`server.ts`). When an external FastAPI backend is configured (`FASTAPI_URL`), requests are transparently proxied; otherwise, all routes are serviced natively by `api_router.ts` using direct Supabase queries.

3. **Event-Driven Cross-Domain Orchestration**:
   When operational events occur (e.g. supplier shipping delay, machinery downtime, or temperature excursion), the **Master Orchestrator** assesses cross-domain propagation across all 4 operational spheres, computes the upstream Bullwhip Effect amplification, and returns actionable mitigation recommendations.

4. **Multi-Persona Role-Based Access Control (RBAC)**:
   Individual domain leaders (Procurement, Inventory, Production, Logistics) are restricted to their functional consoles, while the Operations Director retains full visibility across the Control Tower and all domain views.

---

## 3. Component Details & Data Flow

### 3.1 Presentation Layer (Static HTML5 & Tailwind CSS)
- **`index.html`**: Marketing overview, executive KPI highlights, and solution value proposition.
- **`login.html`**: Multi-persona authentication portal pre-configured for the 5 enterprise roles.
- **`control-tower.html`**: Master decision dashboard with cross-domain status metrics, Bullwhip simulation runner, live disruption feeds, and recommendation approval cards.
- **`procurement.html`**: Purchase order tracking, supplier performance scorecards, contract compliance, and new PO creation.
- **`inventory.html`**: Warehouse stock levels, available vs reserved stock, FEFO shelf-life tracking, and safety stock reorder alerts.
- **`production.html`**: Line throughput, active batch work orders, Bill of Materials (BOM) material explosion, and machine breakdown risk scoring.
- **`logistics.html`**: Inbound shipment manifests, carrier performance, and IoT cold-chain reefer temperature telemetry.

### 3.2 Client Assets & Interaction Engine
- **`assets/api.js`**: Reusable client API abstraction module providing authenticated `fetchWithAuth()` wrappers for all backend routes.
- **`assets/app.js`**: UI controller handling dynamic DOM rendering, session token lifecycle, route-guarding redirects, event listeners, and live polling.

### 3.3 Server & API Gateway Layer
- **`server.ts`**: Entry point running Express on port 3000. Configures CORS, JSON body parsers, static file serving, and the API router.
- **`api_router.ts`**: Native TypeScript implementation of the supply chain API. Implements JWT authentication, database access helpers, cross-domain entity enrichments, and the Master Orchestrator simulation engine.

---

## 4. Entity-Relationship & Domain Models

```
┌──────────────┐         ┌─────────────────────────┐         ┌───────────────────────────┐
│  suppliers   │ 1────*  │     purchase_orders     │ 1────*  │   purchase_order_items    │
└──────┬───────┘         └───────────┬─────────────┘         └─────────────┬─────────────┘
       │                             │                                     │
       │ 1                           │ 1                                   │ *
       ▼ *                           ▼ *                                   ▼ 1
┌──────────────┐         ┌─────────────────────────┐         ┌───────────────────────────┐
│ supplier_    │         │        shipments        │ 1────*  │         products          │
│ performance  │         └───────────┬─────────────┘         └─────────────┬─────────────┘
└──────────────┘                     │                                     │
                                     │ 1                                   │ 1
                                     ▼ *                                   ▼ *
                         ┌─────────────────────────┐         ┌───────────────────────────┐
                         │   temperature_telemetry │         │         inventory         │
                         └─────────────────────────┘         └─────────────┬─────────────┘
                                                                           │ 1
                                                                           ▼ *
                         ┌─────────────────────────┐         ┌───────────────────────────┐
                         │    production_orders    │ 1────*  │      production_bom       │
                         └─────────────────────────┘         └───────────────────────────┘
```

---

## 5. Master Orchestrator & Bullwhip Calculation Engine

The Master Orchestrator (`/api/master/events`) processes disruptions across four sequential phases:

1. **Domain Detection**: Identifies whether the incident originates in Procurement, Inventory, Production, or Logistics.
2. **Forward Impact Propagation**:
   - *Procurement Delay* $\rightarrow$ Depletes warehouse safety stock $\rightarrow$ Delays production batch lines $\rightarrow$ Pushes customer fulfillment deadlines.
   - *Production Bottleneck* $\rightarrow$ Increases WIP holding inventory $\rightarrow$ Backlogs outbound logistics staging.
   - *Cold Chain Excursion* $\rightarrow$ Scraps perishable raw materials $\rightarrow$ Triggers emergency replenishment.
3. **Backward Impact & Bullwhip Amplification**:
   - Calculates the ratio between upstream inventory buffer safety inflations and downstream retail demand variability.
   - Quantifies the financial exposure in USD and computes the risk severity score (0 to 100).
4. **Prescriptive Recommendations**:
   - Generates actionable mitigations (e.g. allocating secondary backup suppliers, rerouting freight carriers, rescheduling work order priorities).
   - Records actions into the database for operator review and approval via `POST /api/recommendations/:id/approve`.
