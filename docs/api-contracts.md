# Supply Chain Management - REST API Contracts
## 1. Authentication
### 1.1 Register User

Method: POST

Endpoint:
/api/auth/register

Purpose:
Create a new user account.

Authentication:
Not required

Request Body:
{
  "email": "user@example.com",
  "password": "password123",
  "full_name": "John Doe"
}

Success Response:
201 Created


### 1.2 Login User

Method: POST

Endpoint:
/api/auth/login

Purpose:
Authenticate a user and return an access token.

Authentication:
Not required

Request Body:
{
  "email": "user@example.com",
  "password": "password123"
}

Success Response:
200 OK


### 1.3 Get Current User

Method: GET

Endpoint:
/api/auth/me

Purpose:
Return the currently authenticated user's profile and role.

Authentication:
Required

Request Body:
None

Success Response:
200 OK


### 1.4 Logout User

Method: POST

Endpoint:
/api/auth/logout

Purpose:
Log out the currently authenticated user.

Authentication:
Required

Request Body:
None

Success Response:
204 No Content

## 2. Products
### 2.1 Get All Products

Method: GET

Endpoint:
/api/products

Purpose:
Get all products.

Authentication:
Required

Request Body:
None

Success Response:
200 OK


### 2.2 Get Product by ID

Method: GET

Endpoint:
/api/products/{product_id}

Purpose:
Get details of a specific product.

Authentication:
Required

Path Parameter:
product_id

Request Body:
None

Success Response:
200 OK


### 2.3 Create Product

Method: POST

Endpoint:
/api/products

Purpose:
Create a new product.

Authentication:
Required

Allowed Roles:
admin

Request Body:
{
  "sku": "MILK-001",
  "name": "Milk",
  "description": "Fresh milk product",
  "category": "Dairy",
  "unit": "litre",
  "reorder_level": 100
}

Success Response:
201 Created


### 2.4 Update Product

Method: PATCH

Endpoint:
/api/products/{product_id}

Purpose:
Update an existing product.

Authentication:
Required

Allowed Roles:
admin

Path Parameter:
product_id

Request Body:
{
  "name": "Updated Milk",
  "reorder_level": 150
}

Success Response:
200 OK


### 2.5 Delete Product

Method: DELETE

Endpoint:
/api/products/{product_id}

Purpose:
Delete a product.

Authentication:
Required

Allowed Roles:
admin

Path Parameter:
product_id

Request Body:
None

Success Response:
204 No Content

## 3. Suppliers
### 3.1 Get All Suppliers

Method: GET

Endpoint:
/api/suppliers

Purpose:
Get all suppliers.

Authentication:
Required

Request Body:
None

Success Response:
200 OK


### 3.2 Get Supplier by ID

Method: GET

Endpoint:
/api/suppliers/{supplier_id}

Purpose:
Get details of a specific supplier.

Authentication:
Required

Path Parameter:
supplier_id

Request Body:
None

Success Response:
200 OK


### 3.3 Create Supplier

Method: POST

Endpoint:
/api/suppliers

Purpose:
Create a new supplier.

Authentication:
Required

Allowed Roles:
admin
procurement

Request Body:
{
  "supplier_code": "SUP-001",
  "name": "Supplier A",
  "contact_person": "John",
  "email": "supplier@example.com",
  "phone": "9876543210",
  "address": "Coimbatore",
  "city": "Coimbatore",
  "country": "India"
}

Success Response:
201 Created


### 3.4 Update Supplier

Method: PATCH

Endpoint:
/api/suppliers/{supplier_id}

Purpose:
Update an existing supplier.

Authentication:
Required

Allowed Roles:
admin
procurement

Path Parameter:
supplier_id

Request Body:
{
  "name": "Updated Supplier A",
  "phone": "9876500000",
  "status": "active"
}

Success Response:
200 OK


### 3.5 Delete Supplier

Method: DELETE

Endpoint:
/api/suppliers/{supplier_id}

Purpose:
Delete or deactivate a supplier.

Authentication:
Required

Allowed Roles:
admin
procurement

Path Parameter:
supplier_id

Request Body:
None

Success Response:
204 No Content
## 4. Inventory
### 4.1 Get All Inventory Balances

Method: GET

Endpoint:
/api/inventory

Purpose:
Retrieve real-time stock balances across all warehouses, cold storage facilities, and distribution centers with enriched product names and SKUs.

Authentication:
Optional / Required for mutations

Query Parameters:
None

Success Response:
200 OK
```json
[
  {
    "id": "inv-001",
    "product_id": "prod-001",
    "warehouse_id": "wh-001",
    "quantity_on_hand": 1200,
    "available_quantity": 950,
    "reserved_quantity": 250,
    "reorder_level": 500,
    "unit": "kg",
    "status": "in_stock",
    "product_name": "Organic Whole Milk Powder",
    "sku": "DAIRY-WMP-01"
  }
]
```

### 4.2 Get Low-Stock Alerts

Method: GET

Endpoint:
/api/inventory/low-stock

Purpose:
Retrieve stock records where available quantity has fallen at or below the configured reorder threshold / safety stock target.

Authentication:
Optional

Success Response:
200 OK

### 4.3 Get Inventory Stream Events

Method: GET

Endpoint:
/api/inventory/events

Purpose:
Retrieve stream transaction events (receipts, issues, reservations, adjustments).

Authentication:
Optional

Success Response:
200 OK

---

## 5. Purchase Orders
### 5.1 Get All Purchase Orders

Method: GET

Endpoint:
/api/purchase-orders

Purpose:
Retrieve all inbound procurement orders with embedded supplier information and itemized line items.

Authentication:
Optional

Success Response:
200 OK
```json
[
  {
    "id": "po-001",
    "po_number": "PO-2026-0891",
    "supplier_id": "sup-001",
    "supplier_name": "Global Lacto Supplies B.V.",
    "status": "confirmed",
    "total_amount": 42500,
    "order_date": "2026-09-01",
    "expected_delivery_date": "2026-09-20",
    "items": [
      {
        "id": "poi-001",
        "purchase_order_id": "po-001",
        "product_id": "prod-001",
        "product_name": "Organic Whole Milk Powder",
        "quantity": 5000,
        "unit_price": 8.5,
        "total_price": 42500
      }
    ]
  }
]
```

### 5.2 Get Purchase Order by ID

Method: GET

Endpoint:
/api/purchase-orders/{id}

Purpose:
Retrieve full details of a specific purchase order by UUID or PO number.

Path Parameter:
`id`: Purchase order UUID or PO number (e.g. `PO-2026-0891`)

Success Response:
200 OK

Error Response:
404 Not Found `{ "detail": "Purchase order not found" }`

### 5.3 Create Purchase Order

Method: POST

Endpoint:
/api/purchase-orders

Purpose:
Create and issue a new purchase order with supplier ID, delivery dates, and line items.

Request Body:
```json
{
  "supplier_id": "sup-001",
  "product_id": "prod-001",
  "quantity": 1000,
  "unit_price": 8.5,
  "expected_delivery_date": "2026-09-25",
  "notes": "Urgent safety stock replenishment"
}
```

Success Response:
201 Created or 200 OK
```json
{
  "message": "Purchase order created successfully",
  "purchase_order": {
    "id": "po-new-uuid",
    "po_number": "PO-54321",
    "status": "ordered",
    "total_amount": 8500
  }
}
```

---

## 6. Production Orders
### 6.1 Get All Production Orders

Method: GET

Endpoint:
/api/production-orders

Purpose:
Retrieve all shop floor manufacturing work orders with associated finished product details.

Authentication:
Optional

Success Response:
200 OK

### 6.2 Get Production Order Details

Method: GET

Endpoint:
/api/production-orders/{id}/details

Purpose:
Retrieve header details, product specification, and manufacturing status.

Success Response:
200 OK

### 6.3 Get Production Order Material Requirements & BOM

Method: GET

Endpoint:
/api/production-orders/{id}/materials

Purpose:
Retrieve Bill of Materials (BOM) explosion, required raw material quantities, and current warehouse stock availability.

Success Response:
200 OK

### 6.4 Get Production Order Progress

Method: GET

Endpoint:
/api/production-orders/{id}/progress

Purpose:
Retrieve batch production telemetry, completed units, reject rate, and active line machine status.

Success Response:
200 OK

### 6.5 Get Production Order Risk Assessment

Method: GET

Endpoint:
/api/production-orders/{id}/risk

Purpose:
Calculate lead time delay and material shortage risk metrics for a production order.

Success Response:
200 OK

### 6.6 Analyze Production Event

Method: POST

Endpoint:
/api/production-orders/analyze-event

Purpose:
Analyze shop floor disruptions (machine breakdown, throughput drop, quality defect) and calculate downstream impacts.

Request Body:
```json
{
  "event_id": "EVT-PRD-01",
  "event_type": "MACHINE_BREAKDOWN",
  "entity_id": "PRD-2026-001",
  "severity": "HIGH",
  "details": "Filling line 2 motor failure"
}
```

Success Response:
200 OK

---

## 7. Shipments & Cold Chain Logistics
### 7.1 Get All Shipments

Method: GET

Endpoint:
/api/shipments

Purpose:
Retrieve all inbound and inter-facility shipments with carrier, origin, destination, and linked PO details.

Authentication:
Optional

Success Response:
200 OK

### 7.2 Get Shipment Details & Telemetry

Method: GET

Endpoint:
/api/shipments/{id}/details

Purpose:
Retrieve manifest line items, warehouse receipts, and IoT temperature telemetry with cold chain excursion analysis.

Success Response:
200 OK
```json
{
  "shipment": { "id": "shp-001", "tracking_number": "TRK-9821" },
  "items": [],
  "receipts": [],
  "telemetry": {
    "telemetry_records": [],
    "cold_chain_status": "NORMAL"
  }
}
```

### 7.3 Analyze Shipment Disruption Event

Method: POST

Endpoint:
/api/shipments/analyze-event

Purpose:
Process transport disruption events (reefer failure, port congestion, customs hold) and quantify delay days and spoiled inventory value.

Request Body:
```json
{
  "event_id": "EVT-LOG-01",
  "event_type": "TEMPERATURE_EXCURSION",
  "entity_id": "shp-001",
  "temperature_reading": 9.4
}
```

Success Response:
200 OK

---

## 8. Cross-Domain Events & Master Orchestrator
### 8.1 Get Event Log

Method: GET

Endpoint:
/api/events

Purpose:
Retrieve operational event logs across Procurement, Inventory, Production, and Logistics.

Query Parameters:
- `limit`: Number of records to return (default: 50)

Success Response:
200 OK

### 8.2 Dispatch Disruption Event (Master Pipeline)

Method: POST

Endpoint:
/api/master/events
/api/master/internal/events

Purpose:
Trigger the master cross-domain decision engine to evaluate cascading forward and backward impacts (Bullwhip Effect), assess risk severity, and produce automated mitigation recommendations.

Request Body:
```json
{
  "event_id": "EVT-1001",
  "event_type": "SUPPLIER_DELAY",
  "source_domain": "Procurement",
  "entity_id": "PO-2026-0891",
  "severity": "HIGH",
  "details": "Port labor strike causing 8 days delay on raw milk powder delivery"
}
```

Success Response:
200 OK
```json
{
  "orchestration_id": "PIPE-EVT-1001-20260917020000",
  "event_id": "EVT-1001",
  "event_type": "SUPPLIER_DELAY",
  "primary_domain": "Procurement",
  "affected_domains": ["Inventory", "Production", "Logistics"],
  "domain_results": [],
  "forward_impact": {
    "procurement": {},
    "inventory": {},
    "production": {},
    "logistics": {}
  },
  "backward_impact": {
    "bullwhip_ratio": 1.45,
    "demand_amplification": "145% upstream variation vs 10% baseline fluctuation",
    "financial_exposure_usd": 128400
  },
  "recommendations": [
    {
      "id": "rec-001",
      "action": "Trigger Tier-2 Alternate Supplier Allocation",
      "status": "PENDING"
    }
  ],
  "overall_risk_score": 88
}
```

### 8.3 Get Latest Master Execution

Method: GET

Endpoint:
/api/master/latest

Purpose:
Retrieve the most recent end-to-end multi-agent pipeline execution result for real-time dashboard binding.

Success Response:
200 OK

### 8.4 Trigger Pre-Configured Test Event

Method: POST

Endpoint:
/api/master/test-event/{eventId}

Path Parameter:
- `eventId`: Test scenario ID (e.g. `EVT-001` for Supplier Delay, `EVT-002` for Production Bottleneck, `EVT-003` for Cold Chain Excursion)

Success Response:
200 OK

---

## 9. Alerts
### 9.1 Get Active Alerts

Method: GET

Endpoint:
/api/alerts

Purpose:
Retrieve prioritized operational alerts with severity levels (`CRITICAL`, `HIGH`, `MEDIUM`, `LOW`) and resolution status.

Success Response:
200 OK

### 9.2 Acknowledge Alert

Method: POST

Endpoint:
/api/alerts/{id}/acknowledge

Purpose:
Acknowledge an active alert and mark it as reviewed in the database.

Path Parameter:
`id`: Alert UUID

Success Response:
200 OK `{ "message": "Alert acknowledged", "id": "alert-id" }`

---

## 10. Operational Risks
### 10.1 Get Active Risk Log

Method: GET

Endpoint:
/api/risks

Purpose:
Retrieve quantifiable supply chain risks, impact likelihoods, financial exposures, and bullwhip amplification factors.

Success Response:
200 OK

---

## 11. Decision Recommendations
### 11.1 Get Active Recommendations

Method: GET

Endpoint:
/api/recommendations

Purpose:
Retrieve AI-generated and rule-based prescriptive actions proposed by the domain agents.

Success Response:
200 OK

### 11.2 Approve Recommendation

Method: POST

Endpoint:
/api/recommendations/{id}/approve

Purpose:
Approve a recommended mitigation action (e.g. reroute logistics carrier, trigger backup purchase order, adjust production line).

Path Parameter:
`id`: Recommendation UUID

Success Response:
200 OK `{ "message": "Recommendation approved", "id": "rec-id", "status": "APPROVED" }`

---

# Common API Rules

## Base URL

`/api`

## Authentication

Protected APIs require a valid Bearer authentication token issued by `/api/auth/login` or `/api/auth/register`:
```http
Authorization: Bearer <access_token>
```

## Standard HTTP Methods

- `GET`    - Read entity or collection
- `POST`   - Create resource or execute event analysis
- `PATCH`  - Update resource fields
- `DELETE` - Remove resource

## Standard Success Status Codes

- `200 OK` - Request succeeded and response contains payload
- `201 Created` - Resource created successfully
- `204 No Content` - Operation completed without payload

## Standard Error Status Codes

- `400 Bad Request` - Validation failure or missing required fields
- `401 Unauthorized` - Missing, invalid, or expired session token
- `403 Forbidden` - Insufficient role permissions for requested action
- `404 Not Found` - Entity or resource does not exist
- `503 Service Unavailable` - Database connection or downstream service unavailable

## API Module Structure

| Category | Endpoint Prefix | Primary Responsibilities |
| :--- | :--- | :--- |
| **Authentication** | `/api/auth` | User login, registration, session validation, and logout |
| **Products** | `/api/products` | Finished goods and raw material catalog management |
| **Suppliers** | `/api/suppliers` | Global vendor registry, scorecards, and contracts |
| **Inventory** | `/api/inventory` | Real-time stock levels, reorder thresholds, and events |
| **Purchase Orders** | `/api/purchase-orders` | Inbound orders, order items, and procurement creation |
| **Production Orders**| `/api/production-orders`| Manufacturing orders, BOM requirements, and line progress |
| **Shipments** | `/api/shipments` | Transport manifests, delivery receipts, and IoT temperature |
| **Master Orchestrator**| `/api/master` | Multi-agent event processing, Bullwhip effect, and impact analysis |
| **Alerts & Risks** | `/api/alerts`, `/api/risks`| Operational exception triaging and vulnerability monitoring |
| **Recommendations** | `/api/recommendations` | Automated prescriptive decision workflows and approvals |