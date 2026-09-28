import fs from 'fs';

let content = fs.readFileSync('api_router.ts', 'utf8');

// Find where auth routes start
const authIdx = content.indexOf('// ==========================================\n// AUTH ROUTES');

if (authIdx !== -1) {
  // Check if there are master routes after auth routes or duplicated master routes before auth
  const masterStartIdx = content.indexOf('apiRouter.get(\'/master/status\'');
  const masterSecondIdx = content.indexOf('apiRouter.get(\'/master/status\'', masterStartIdx + 10);
  
  if (masterSecondIdx !== -1) {
    // Keep only up to masterSecondIdx, then append auth routes
    content = content.slice(0, masterSecondIdx) + content.slice(authIdx);
  }
}

// Remove any lingering VERIFIED_PROCUREMENT_MASTER_RESPONSE references
content = content.replace(/VERIFIED_PROCUREMENT_MASTER_RESPONSE/g, 'buildMasterPipelineResponse({ event_id: "EVT-TEST-004", event_type: "SUPPLIER_DELAY" })');

fs.writeFileSync('api_router.ts', content);
console.log('Fixed router duplicates');
