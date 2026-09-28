# Nexus Tower: Operations Runbook & Deployment Guide

## 1. Quick Start

### 1.1 Prerequisites
- Node.js 20+ / 22+
- npm or bun

### 1.2 Development Mode
To start the local development server on port 3000 with live auto-reload:
```bash
npm run dev
```

### 1.3 Production Execution
To compile and launch the production server:
```bash
npm run build
npm start
```

---

## 2. Health & Diagnostic Endpoints

### 2.1 API Gateway & Database Health
```bash
curl -s http://localhost:3000/api/health
```
Response:
```json
{
  "status": "healthy",
  "database": "connected",
  "timestamp": "2026-09-17T02:04:15.433Z",
  "service": "NexusTower-API-Gateway"
}
```

### 2.2 Server Process Health
```bash
curl -s http://localhost:3000/health
```
Response:
```json
{
  "status": "ok",
  "gateway": "Nexus Tower Server",
  "mode": "Native",
  "timestamp": "2026-09-17T02:04:15.433Z",
  "uptime_seconds": 184.2
}
```

---

## 3. Disruption Simulation & Event Triggering

The platform includes a synthetic scenario engine allowing operators and automated tests to inject disruptions and observe cross-domain propagation.

### 3.1 Pre-Packaged Test Scenarios
To trigger a pre-packaged cross-domain scenario:
```bash
# EVT-001: Raw Material Supplier Lead Time Delay
curl -X POST http://localhost:3000/api/master/test-event/EVT-001

# EVT-002: Bottling & Packaging Line Breakdown
curl -X POST http://localhost:3000/api/master/test-event/EVT-002

# EVT-003: Cold Chain Reefer Temperature Excursion
curl -X POST http://localhost:3000/api/master/test-event/EVT-003
```

### 3.2 Custom Disruption Event
To inject an arbitrary event into the Master Orchestrator:
```bash
curl -X POST http://localhost:3000/api/master/events \
  -H "Content-Type: application/json" \
  -d '{
    "event_id": "EVT-SIM-901",
    "event_type": "SUPPLIER_DELAY",
    "source_domain": "Procurement",
    "entity_id": "PO-001",
    "severity": "HIGH",
    "details": "Major typhoon impacting ocean freight carrier on trans-pacific lane"
  }'
```

---

## 4. API cURL Cheat Sheet

### 4.1 Authenticate & Obtain Token
```bash
TOKEN=$(curl -s -X POST http://localhost:3000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"m.vance@nexustower.internal","password":"password123"}' \
  | grep -o '"access_token":"[^"]*' | cut -d'"' -f4)
echo "Token: $TOKEN"
```

### 4.2 Query Low Stock
```bash
curl -s http://localhost:3000/api/inventory/low-stock \
  -H "Authorization: Bearer $TOKEN"
```

### 4.3 Create a Purchase Order
```bash
curl -s -X POST http://localhost:3000/api/purchase-orders \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "supplier_id": "sup-001",
    "product_id": "prod-001",
    "quantity": 1200,
    "unit_price": 8.5,
    "expected_delivery_date": "2026-09-30",
    "notes": "Triggered via CLI replenishment"
  }'
```

### 4.4 Approve Recommendation
```bash
curl -s -X POST http://localhost:3000/api/recommendations/rec-001/approve \
  -H "Authorization: Bearer $TOKEN"
```

---

## 5. Troubleshooting & FAQ

| Symptom | Cause | Remedy |
| :--- | :--- | :--- |
| `database: "disconnected"` in `/api/health` | Missing or invalid `SUPABASE_URL` / `SUPABASE_SECRET_KEY` | Check `.env` configuration. If running offline, gateway uses synthetic fallback datasets automatically. |
| `HTTP 401 Unauthorized` on protected routes | Expired or missing Bearer token | Re-authenticate via `/api/auth/login` or re-login in `login.html`. |
| Role navigation redirecting to wrong page | User session contains non-admin persona role | Log out and switch to Operations Director (`ops-admin@nexustower.internal`) for unrestricted navigation. |
| Browser displays cached styles or layouts | Browser cache stale | Perform hard refresh (`Cmd+Shift+R` or `Ctrl+F5`). |
