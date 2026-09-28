# Nexus Tower: FMCG Supply Chain Operations Cockpit

Nexus Tower is an enterprise supply chain operations cockpit and decision intelligence platform for FMCG manufacturing networks. It integrates four core operational domains—**Procurement**, **Inventory**, **Production**, and **Logistics**—with an autonomous cross-domain **Master Orchestrator**, real-time Bullwhip Effect quantification, and prescriptive mitigation workflows.

---

## 🚀 Key Capabilities

- **Unified Operations Cockpit**: Single-pane-of-glass executive visibility across all supply chain tiers.
- **Cross-Domain Master Orchestrator**: Event-driven engine calculating cascading forward impacts and backward Bullwhip demand amplifications.
- **Role-Based Access Control (RBAC)**: Five discrete operational personas with route gating and persona-specific dashboards.
- **Zero-Trust Security**: Server-side credential isolation (Supabase secret keys never exposed to the client), signed session tokens, and input sanitization.
- **Cold Chain & IoT Telemetry**: Reefer temperature tracking, excursion analysis, and automatic scrap inventory quantification.

---

## 📂 Cockpit Applications & Consoles

| Console | URL / File | Purpose |
| :--- | :--- | :--- |
| **Landing Page** | `index.html` / `/` | Solution architecture, executive summary, and platform overview |
| **Authentication Portal** | `login.html` / `/login` | Enterprise login with 1-click persona switching |
| **Control Tower** | `control-tower.html` / `/control-tower` | Master decision cockpit, Bullwhip simulator, and recommendation approvals |
| **Procurement** | `procurement.html` / `/procurement` | Inbound purchase orders, supplier scorecards, and contract compliance |
| **Inventory** | `inventory.html` / `/inventory` | Warehouse balances, FEFO shelf-life tracking, and safety stock reorder levels |
| **Production** | `production.html` / `/production` | Line throughput, active batch work orders, and BOM material explosions |
| **Logistics** | `logistics.html` / `/logistics` | Inbound manifests, carrier performance, and IoT temperature telemetry |

---

## 👥 Demo Personas & Credentials

All test accounts share the default password: `password123`.

| Name | Role | Email | Default Console |
| :--- | :--- | :--- | :--- |
| **Marcus Vance** | Procurement Lead | `m.vance@nexustower.internal` | `/procurement` |
| **Sarah Chen** | Inventory Lead | `s.chen@nexustower.internal` | `/inventory` |
| **Karel Novak** | Production Lead | `k.novak@nexustower.internal` | `/production` |
| **Elena Morales** | Logistics Lead | `d.morales@nexustower.internal` | `/logistics` |
| **David Rossi** | Operations Director | `ops-admin@nexustower.internal` | `/control-tower` (Full access) |

---

## 🛠️ Getting Started

### Development
```bash
npm run dev
```
Launches the Express API Gateway and static file server at `http://localhost:3000`.

### Production Build & Run
```bash
npm run build
npm start
```

### Health Check
```bash
curl -s http://localhost:3000/api/health
```

---

## 📚 Technical Documentation

- **[Architecture & Systems Guide](docs/architecture.md)**: Deep dive into the platform topology, data flows, and Master Orchestrator engine.
- **[REST API Contracts](docs/api-contracts.md)**: Full endpoint specification across Authentication, Products, Suppliers, Inventory, POs, Production, Shipments, Events, and Alerts.
- **[Security & RBAC Matrix](docs/security-and-rbac.md)**: Role permissions, session lifecycle, token handling, and security hardening rules.
- **[Operations Runbook](docs/operations-and-runbook.md)**: Deployment guidelines, diagnostics, simulation event triggers, and cURL recipes.
- **[Dataset Catalog](dataset/README.md)**: Synthetic FMCG data specifications, schema tables, and relational seed records.

