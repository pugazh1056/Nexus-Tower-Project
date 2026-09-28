import fs from 'fs';

let api = fs.readFileSync('assets/api.js', 'utf8');
api = api.replace(/async triggerMasterTestEvent\(eventId = 'EVT-TEST-004'\) \{[\s\S]*?\}/, `async triggerMasterTestEvent(eventId = 'EVT-TEST-004') {
      const payloadMap = {
        'SUPPLIER_DELAY': { event_id: 'EVT-SUP-01', event_type: 'SUPPLIER_DELAY', source_domain: 'Procurement', entity_type: 'purchase_order', entity_id: 'PO-001' },
        'STOCK_LOW': { event_id: 'EVT-INV-01', event_type: 'STOCK_LOW', source_domain: 'Inventory', entity_type: 'product', entity_id: 'PRD-001' },
        'PRODUCTION_DISRUPTION': { event_id: 'EVT-PROD-01', event_type: 'PRODUCTION_DISRUPTION', source_domain: 'Production', entity_type: 'production_order', entity_id: 'PROD-001' },
        'SHIPMENT_DISRUPTION': { event_id: 'EVT-LOG-01', event_type: 'SHIPMENT_DISRUPTION', source_domain: 'Logistics', entity_type: 'shipment', entity_id: 'SHP-001' }
      };
      
      const payload = payloadMap[eventId] || payloadMap['SUPPLIER_DELAY'];
      return this.request('/master/internal/events', {
        method: 'POST',
        body: payload,
      });
    }`);

fs.writeFileSync('assets/api.js', api);
console.log('patched api.js');
