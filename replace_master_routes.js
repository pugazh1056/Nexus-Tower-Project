import fs from 'fs';

let content = fs.readFileSync('api_router.ts', 'utf8');

const marker = '// MASTER AGENT ROUTES';
const idx = content.indexOf(marker);

if (idx !== -1) {
  const replacement = `// MASTER AGENT ROUTES
// ==========================================
apiRouter.get('/master/status', (_req: Request, res: Response) => {
  const webhookUrl = process.env.MASTER_WEBHOOK_URL;
  res.json({
    status: 'operational',
    service: 'MasterAgentIntegrationService',
    webhook_configured: !!webhookUrl,
    latest_event_id: latestMasterExecution?.event_id || 'EVT-NONE',
    latest_execution_id: latestMasterExecution?.pipeline_execution_id || 'EXEC-NONE',
  });
});

apiRouter.get('/master/latest', (_req: Request, res: Response) => {
  if (!latestMasterExecution) {
    latestMasterExecution = buildMasterPipelineResponse({ event_id: 'EVT-SUP-01', event_type: 'SUPPLIER_DELAY' });
  }
  res.json(latestMasterExecution);
});

apiRouter.post('/master/internal/events', async (req: Request, res: Response) => {
  const event = req.body || {};
  const webhookUrl = process.env.MASTER_WEBHOOK_URL;
  if (webhookUrl) {
    try {
      const response = await fetch(webhookUrl, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(event),
      });
      if (response.ok) {
        const result = await response.json();
        latestMasterExecution = result;
        return res.json(result);
      }
    } catch (err: any) {
      console.error('[Master Webhook Dispatch Error]:', err);
    }
  }
  latestMasterExecution = buildMasterPipelineResponse(event);
  res.json(latestMasterExecution);
});

apiRouter.post('/master/events', async (req: Request, res: Response) => {
  const event = req.body || {};
  const webhookUrl = process.env.MASTER_WEBHOOK_URL;
  if (webhookUrl) {
    try {
      const response = await fetch(webhookUrl, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(event),
      });
      if (response.ok) {
        const result = await response.json();
        latestMasterExecution = result;
        return res.json(result);
      }
    } catch (err: any) {
      console.error('[Master Webhook Dispatch Error]:', err);
    }
  }
  latestMasterExecution = buildMasterPipelineResponse(event);
  res.json(latestMasterExecution);
});

apiRouter.post('/master/test-event/:eventId', async (req: Request, res: Response) => {
  const { eventId } = req.params;
  const eventPayload = {
    event_id: eventId || 'EVT-SUP-01',
    event_type: eventId === 'STOCK_LOW' ? 'STOCK_LOW' : eventId === 'PRODUCTION_DISRUPTION' ? 'PRODUCTION_DISRUPTION' : eventId === 'SHIPMENT_DISRUPTION' ? 'SHIPMENT_DISRUPTION' : 'SUPPLIER_DELAY',
    source_domain: eventId === 'STOCK_LOW' ? 'Inventory' : eventId === 'PRODUCTION_DISRUPTION' ? 'Production' : eventId === 'SHIPMENT_DISRUPTION' ? 'Logistics' : 'Procurement',
    entity_type: 'purchase_order',
    entity_id: 'PO-001'
  };
  latestMasterExecution = buildMasterPipelineResponse(eventPayload);
  res.json(latestMasterExecution);
});
`;

  content = content.slice(0, idx) + replacement;
}

fs.writeFileSync('api_router.ts', content);
console.log('Replaced master routes successfully');
