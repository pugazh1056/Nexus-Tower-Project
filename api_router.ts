import express, { Request, Response, Router } from 'express';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const datasetDir = path.join(__dirname, 'dataset');

export const apiRouter: Router = express.Router();

// Helper to parse simple CSV files into array of objects
function parseCsv(filename: string): any[] {
  try {
    const filePath = path.join(datasetDir, filename);
    if (!fs.existsSync(filePath)) return [];
    const content = fs.readFileSync(filePath, 'utf-8');
    const lines = content.trim().split('\n');
    if (lines.length < 2) return [];

    const headers = lines[0].split(',').map((h) => h.trim());
    return lines.slice(1).map((line) => {
      const values = line.split(',').map((v) => v.trim());
      const row: Record<string, any> = {};
      headers.forEach((h, i) => {
        let val: any = values[i];
        if (val === 'True') val = true;
        else if (val === 'False') val = false;
        else if (!isNaN(Number(val)) && val !== '') val = Number(val);
        row[h] = val;
      });
      return row;
    });
  } catch (err) {
    console.error(`Error reading ${filename}:`, err);
    return [];
  }
}

// In-memory data store initialized from dataset
const products = parseCsv('products.csv');
const inventory = parseCsv('inventory.csv');
const suppliers = parseCsv('suppliers.csv');
const purchaseOrders = parseCsv('purchase_orders.csv');
const poItems = parseCsv('purchase_order_items.csv');
const productionOrders = parseCsv('production_orders.csv');
const shipments = parseCsv('shipments.csv');
const events = parseCsv('events.csv');

// Default Demo User Profiles
const DEFAULT_PROFILES: Record<string, any> = {
  'm.vance@nexustower.internal': {
    id: 'usr-proc-001',
    email: 'm.vance@nexustower.internal',
    full_name: 'Marcus Vance',
    role: 'procurement',
    role_name: 'procurement',
  },
  's.chen@nexustower.internal': {
    id: 'usr-invt-002',
    email: 's.chen@nexustower.internal',
    full_name: 'Sarah Chen',
    role: 'inventory',
    role_name: 'inventory',
  },
  'k.novak@nexustower.internal': {
    id: 'usr-prod-003',
    email: 'k.novak@nexustower.internal',
    full_name: 'Klaus Novak',
    role: 'production',
    role_name: 'production',
  },
  'd.morales@nexustower.internal': {
    id: 'usr-logs-004',
    email: 'd.morales@nexustower.internal',
    full_name: 'Diego Morales',
    role: 'logistics',
    role_name: 'logistics',
  },
  'ops-admin@nexustower.internal': {
    id: 'usr-admin-000',
    email: 'ops-admin@nexustower.internal',
    full_name: 'Operations Director',
    role: 'admin',
    role_name: 'admin',
  },
};

// Initial state for alerts, risks, recommendations
let inMemoryAlerts = [
  {
    id: 'ALT-2026-001',
    severity: 'HIGH',
    title: 'Supplier Delay: Dairy Pure Co',
    message: 'Consignment PO-001 delayed by 8 days due to refrigeration unit failure.',
    domain: 'Procurement',
    is_active: true,
    acknowledged: false,
    created_at: '2026-09-15T08:30:00Z',
  },
  {
    id: 'ALT-2026-002',
    severity: 'MEDIUM',
    title: 'Inventory Runway Deficit: Milk Feedstock',
    message: 'Cold Hub Alpha Silo 1 buffer is down to 28.8 hours runway.',
    domain: 'Inventory',
    is_active: true,
    acknowledged: false,
    created_at: '2026-09-15T09:15:00Z',
  },
  {
    id: 'ALT-2026-003',
    severity: 'HIGH',
    title: 'Production Line Starvation Hazard',
    message: 'PRD-2026-001 Pasteurization Line 1 risks idling in 36 hours.',
    domain: 'Production',
    is_active: true,
    acknowledged: false,
    created_at: '2026-09-15T10:00:00Z',
  },
];

let inMemoryRisks = [
  {
    id: 'RSK-2026-001',
    risk_type: 'SUPPLIER_DELAY',
    severity: 'HIGH',
    probability: 0.95,
    financial_impact: 14200.0,
    domain: 'Procurement',
    description: 'Raw Milk feedstock disruption from Supplier A impacting Line 1.',
  },
  {
    id: 'RSK-2026-002',
    risk_type: 'BUFFER_RUNWAY_SHORTAGE',
    severity: 'HIGH',
    probability: 0.88,
    financial_impact: 8500.0,
    domain: 'Inventory',
    description: 'Safety stock below 100L critical threshold for pasteurization.',
  },
];

let inMemoryRecommendations = [
  {
    id: 'REC-2026-001',
    title: 'Emergency Feedstock Reallocation & Alternative Supplier PO',
    description: 'Procure 800L of raw milk from pre-audited Apex Dairy Farms (SUP-005) with expedited cold-chain logistics.',
    action_strategy: 'EXPEDITE_ALTERNATIVE_SUPPLIER',
    confidence_score: 0.96,
    expected_impact: '$14,200 revenue protected • Line 1 continuity',
    status: 'PENDING',
    created_at: '2026-09-15T10:30:00Z',
  },
];

// Reference Verified Master Pipeline Execution Contract for EVT-TEST-004
const VERIFIED_MASTER_EXECUTION = {
  pipeline_execution_id: 'EXEC-MST-2026-0915-004',
  event_id: 'EVT-TEST-004',
  status: 'COMPLETED',
  timestamp: '2026-09-15T18:45:00Z',
  stages: {
    normalization: {
      source_domain: 'Procurement Agent',
      event_type: 'SUPPLIER_DELAY',
      entity_id: 'PO-001',
      supplier: {
        name: 'Dairy Pure Co',
        supplier_code: 'SUP-001',
      },
      product: {
        sku: 'MILK-001',
        name: 'Fresh Cow Milk',
      },
      delay_parameters: {
        delay_days: 8,
        original_expected_date: '2026-09-06',
        revised_expected_date: '2026-09-14',
      },
    },
    priority: {
      severity: 'HIGH',
      urgency_score: 92.4,
      sla_impact: 'BREACH_IMMINENT',
      justification: '8-day delay on primary feedstock with single-silo buffer below 38h threshold.',
    },
    backward_impact: {
      root_cause: 'Refrigeration compressor breakdown during pre-transit milk chilling',
      historical_supplier_performance: {
        on_time_delivery_rate: 0.75,
        average_lead_time_days: 3.5,
        defect_rate: 0.012,
        total_historical_orders: 4,
      },
      contract_audit: {
        contract_id: 'CTR-SUP001-2026',
        sla_minimum: 0.95,
        applicable_penalty_amount: 800.0,
      },
    },
    forward_impact: {
      affected_domains: ['Inventory', 'Production', 'Logistics'],
      inventory_impact: {
        current_available_quantity: 30.0,
        runway_hours: 28.8,
        safety_threshold: 100.0,
        deficit: 70.0,
      },
      production_impact: {
        affected_order_id: 'PRD-2026-001',
        impacted_line: 'Pasteurization Line 1',
        feedstock_required: 840.0,
        material_shortage: 795.0,
        starvation_hazard: 'CRITICAL IDLE RISK',
      },
      logistics_fulfillment_impact: {
        impacted_distribution_centers: ['DC-North', 'DC-Metro'],
        estimated_revenue_at_risk: 14200.0,
        fill_rate_projection_without_action: 0.42,
      },
    },
    demand_forecasting_gate: {
      sku: 'MILK-001',
      daily_consumption_rate: 25.0,
      projected_7_day_demand: 175.0,
      projected_14_day_demand: 350.0,
      safety_stock_threshold: 100.0,
      gate_status: 'THRESHOLD_BREACHED',
      decision_gate: 'PASSED_TO_OPTIMIZER',
    },
    decision_optimization: {
      evaluated_options: [
        {
          option_id: 'OPT-1',
          strategy: 'EXPEDITE_ALTERNATIVE_SUPPLIER',
          cost: 1200.0,
          production_downtime_loss: 0.0,
          net_financial_impact: 13000.0,
          otif_projection: 0.98,
          score: 94.5,
        },
        {
          option_id: 'OPT-2',
          strategy: 'SPLIT_BATCH_PRODUCTION',
          cost: 450.0,
          production_downtime_loss: 3200.0,
          net_financial_impact: 10550.0,
          otif_projection: 0.81,
          score: 82.0,
        },
        {
          option_id: 'OPT-3',
          strategy: 'NO_ACTION_WAIT_FOR_SUPPLIER',
          cost: 0.0,
          production_downtime_loss: 14200.0,
          net_financial_impact: -14200.0,
          otif_projection: 0.42,
          score: 28.0,
        },
      ],
      selected_recommendation: {
        action_strategy: 'EXPEDITE_ALTERNATIVE_SUPPLIER',
        title: 'Emergency Feedstock Reallocation',
        description: 'Secure 800L of pasteurization feedstock from pre-audited Apex Dairy Farms (SUP-005) with 48h SLA delivery window.',
        confidence_score: 0.96,
        net_protected_value: 13000.0,
      },
    },
    smart_replenishment: {
      status: 'PROPOSED_PENDING_APPROVAL',
      supplier: {
        name: 'Apex Dairy Farms',
        supplier_code: 'SUP-005',
        tier: 'TIER_1_BACKUP',
        lead_time_days: 2,
      },
      replenishment_item: {
        sku: 'RAW-MILK-01',
        name: 'Raw Pasteurization Feedstock',
        quantity: 800.0,
        unit: 'Liters',
        unit_price: 37.0,
        total_amount: 29600.0,
        currency: 'USD',
      },
      estimated_delivery_date: '2026-09-18',
      requisition_id: 'REQ-AUTO-2026-004',
    },
    execution_boundary: {
      execution_mode: 'HUMAN_IN_THE_LOOP',
      authorized_roles: ['Operations Director', 'Procurement Manager', 'Control Tower Admin'],
      status: 'AWAITING_AUTHORIZATION',
      executable_actions: [
        {
          action_type: 'CREATE_PURCHASE_ORDER',
          endpoint: '/api/purchase-orders/',
          method: 'POST',
          payload: {
            po_number: 'PO-EMERGENCY-001',
            supplier_id: 'SUP-005',
            status: 'draft',
            total_amount: 29600.0,
            expected_delivery_date: '2026-09-18',
            notes: 'Emergency allocation triggered by Master Agent for EVT-TEST-004',
            items: [
              {
                product_id: 'c5e6f7a8-1111-4b2c-8d3e-4f5a6b7c8d9e',
                quantity: 800.0,
                unit_price: 37.0,
              },
            ],
          },
        },
        {
          action_type: 'BROADCAST_OPERATIONAL_ALERT',
          endpoint: '/api/alerts/',
          method: 'POST',
          payload: {
            title: 'Raw Milk Feedstock Expedite Dispatched',
            message: 'Apex Dairy Farms backup PO created. Delivery ETA 2026-09-18. Pasteurization Line 1 saved from idling.',
            severity: 'LOW',
            domain: 'Procurement',
          },
        },
      ],
    },
  },
};

let latestMasterExecution = { ...VERIFIED_MASTER_EXECUTION };

// ==========================================
// AUTH ROUTES
// ==========================================
apiRouter.post('/auth/login', (req: Request, res: Response) => {
  const email = (req.body.email || '').toLowerCase().trim();
  const user = DEFAULT_PROFILES[email] || {
    id: `usr-${Math.floor(Math.random() * 9000) + 1000}`,
    email: email || 'user@nexustower.internal',
    full_name: email.split('@')[0].replace('.', ' ').replace(/\b\w/g, (c: string) => c.toUpperCase()) || 'Operator',
    role: email.includes('admin') ? 'admin' : email.includes('invt') ? 'inventory' : email.includes('prod') ? 'production' : email.includes('logs') ? 'logistics' : 'procurement',
  };

  const encoded = Buffer.from(email).toString('base64');
  const token = `nexus_jwt_${encoded}_sig`;

  res.json({
    access_token: token,
    token_type: 'bearer',
    user,
  });
});

apiRouter.post('/auth/register', (req: Request, res: Response) => {
  const { email, full_name, role } = req.body;
  const user = {
    id: `usr-${Math.floor(Math.random() * 9000) + 1000}`,
    email: (email || '').toLowerCase().trim(),
    full_name: full_name || 'New Operator',
    role: role || 'procurement',
  };

  DEFAULT_PROFILES[user.email] = user;
  const encoded = Buffer.from(user.email).toString('base64');
  res.json({
    access_token: `nexus_jwt_${encoded}_sig`,
    token_type: 'bearer',
    user,
  });
});

apiRouter.get('/auth/me', (req: Request, res: Response) => {
  const authHeader = req.headers.authorization;
  if (!authHeader) {
    return res.status(401).json({ detail: 'Not authenticated' });
  }
  const token = authHeader.replace('Bearer ', '');
  try {
    const parts = token.split('_');
    if (parts.length >= 3) {
      const email = Buffer.from(parts[2], 'base64').toString('utf-8');
      const user = DEFAULT_PROFILES[email] || {
        id: 'usr-001',
        email,
        full_name: email.split('@')[0],
        role: 'procurement',
      };
      return res.json(user);
    }
  } catch (e) {
    // fallback
  }
  res.json(DEFAULT_PROFILES['m.vance@nexustower.internal']);
});

apiRouter.post('/auth/logout', (_req: Request, res: Response) => {
  res.json({ message: 'Successfully logged out' });
});

// ==========================================
// CORE DOMAIN ROUTES
// ==========================================
apiRouter.get('/health', (_req: Request, res: Response) => {
  res.json({
    status: 'healthy',
    timestamp: new Date().toISOString(),
    service: 'NexusTower-API-Gateway',
  });
});

apiRouter.get('/products', (_req: Request, res: Response) => {
  res.json(products);
});

apiRouter.get('/inventory', (_req: Request, res: Response) => {
  res.json(inventory);
});

apiRouter.get('/inventory/low-stock', (_req: Request, res: Response) => {
  const low = inventory.filter((item: any) => (item.available_quantity || 0) <= (item.target_stock || 100));
  res.json(low);
});

apiRouter.get('/suppliers', (_req: Request, res: Response) => {
  res.json(suppliers);
});

apiRouter.get('/purchase-orders', (_req: Request, res: Response) => {
  const enrichedPos = purchaseOrders.map((po: any) => {
    const items = poItems.filter((poi: any) => poi.purchase_order_id === po.id);
    return {
      ...po,
      items: items.length > 0 ? items : [{ product_name: 'Raw Material Feedstock', quantity: 800 }],
    };
  });
  res.json(enrichedPos);
});

apiRouter.post('/purchase-orders', (req: Request, res: Response) => {
  const newPo = {
    id: `PO-${Date.now().toString().slice(-6)}`,
    ...req.body,
    created_at: new Date().toISOString(),
  };
  purchaseOrders.unshift(newPo);
  res.status(201).json(newPo);
});

apiRouter.get('/production-orders', (_req: Request, res: Response) => {
  res.json(productionOrders);
});

apiRouter.get('/shipments', (_req: Request, res: Response) => {
  res.json(shipments);
});

apiRouter.get('/alerts', (_req: Request, res: Response) => {
  res.json(inMemoryAlerts);
});

apiRouter.post('/alerts', (req: Request, res: Response) => {
  const newAlert = {
    id: `ALT-${Date.now().toString().slice(-6)}`,
    ...req.body,
    is_active: true,
    acknowledged: false,
    created_at: new Date().toISOString(),
  };
  inMemoryAlerts.unshift(newAlert);
  res.status(201).json(newAlert);
});

apiRouter.post('/alerts/:id/acknowledge', (req: Request, res: Response) => {
  const { id } = req.params;
  const alert = inMemoryAlerts.find((a) => a.id === id);
  if (alert) alert.acknowledged = true;
  res.json({ message: 'Alert acknowledged', id });
});

apiRouter.get('/risks', (_req: Request, res: Response) => {
  res.json(inMemoryRisks);
});

apiRouter.get('/recommendations', (_req: Request, res: Response) => {
  res.json(inMemoryRecommendations);
});

apiRouter.post('/recommendations/:id/approve', (req: Request, res: Response) => {
  const { id } = req.params;
  const rec = inMemoryRecommendations.find((r) => r.id === id);
  if (rec) rec.status = 'APPROVED';
  res.json({ message: 'Recommendation approved', id, status: 'APPROVED' });
});

apiRouter.get('/events', (req: Request, res: Response) => {
  const limit = parseInt(req.query.limit as string, 10) || 20;
  res.json(events.slice(0, limit));
});

// ==========================================
// MASTER AGENT ROUTES
// ==========================================
apiRouter.get('/master/status', (_req: Request, res: Response) => {
  const webhookUrl = process.env.MASTER_WEBHOOK_URL;
  res.json({
    status: 'operational',
    service: 'MasterAgentIntegrationService',
    webhook_configured: !!webhookUrl,
    latest_event_id: latestMasterExecution.event_id,
    latest_execution_id: latestMasterExecution.pipeline_execution_id,
  });
});

apiRouter.get('/master/latest', (_req: Request, res: Response) => {
  res.json(latestMasterExecution);
});

apiRouter.post('/master/test-event/:eventId', (req: Request, res: Response) => {
  const { eventId } = req.params;
  if (eventId !== 'EVT-TEST-004') {
    return res.status(404).json({ detail: `Test event '${eventId}' not found.` });
  }

  const updatedExecution = {
    ...VERIFIED_MASTER_EXECUTION,
    timestamp: new Date().toISOString(),
  };
  latestMasterExecution = updatedExecution;
  res.json(updatedExecution);
});

apiRouter.post('/master/events', async (req: Request, res: Response) => {
  const event = req.body;
  const webhookUrl = process.env.MASTER_WEBHOOK_URL;

  if (webhookUrl) {
    try {
      const response = await fetch(webhookUrl, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(event),
      });

      if (!response.ok) {
        const errorText = await response.text();
        return res.status(response.status).json({
          detail: `Master Webhook responded with status ${response.status}: ${errorText}`,
        });
      }

      const result = await response.json();
      latestMasterExecution = result;
      return res.json(result);
    } catch (err: any) {
      console.error('[Master Webhook Dispatch Error]:', err);
      return res.status(502).json({
        detail: `Failed to connect to Master Agent webhook: ${err.message}`,
      });
    }
  }

  // Reference execution mode when MASTER_WEBHOOK_URL is not configured
  const mockExecution = {
    ...VERIFIED_MASTER_EXECUTION,
    event_id: event.event_id || 'EVT-SUBMITTED-001',
    pipeline_execution_id: `EXEC-MST-${Date.now()}`,
    timestamp: new Date().toISOString(),
  };
  latestMasterExecution = mockExecution;
  res.json(mockExecution);
});
