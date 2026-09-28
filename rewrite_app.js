import fs from 'fs';

let js = fs.readFileSync('assets/app.js', 'utf8');

const newRenderFn = `
  const renderMasterPipeline = (data) => {
    if (!data) return;

    let unwrapped = data;
    if (unwrapped.master_response) unwrapped = unwrapped.master_response;
    if (unwrapped.raw_response && typeof unwrapped.raw_response === 'object') {
      unwrapped = unwrapped.raw_response;
    }

    const {
      pipeline_execution_id = 'N/A',
      event_id = 'UNKNOWN',
      status = 'UNKNOWN',
      source_domain = 'Unknown',
      primary_domain = 'Unknown',
      approval_status = 'PENDING',
      forward_impact = {},
      backward_impact = {},
      recommendations = [],
      affected_domains = [],
      domain_results = []
    } = unwrapped;

    document.getElementById('pipeline-status-badge').textContent = \`STATUS: \${status.toUpperCase()}\`;
    document.getElementById('pipeline-event-id').textContent = event_id;
    document.getElementById('pipeline-exec-id').textContent = pipeline_execution_id;
    document.getElementById('pipeline-source-domain').textContent = source_domain;
    document.getElementById('pipeline-primary-domain').textContent = primary_domain;
    document.getElementById('pipeline-approval-status').textContent = approval_status;
    
    // Forward Impact
    const fwContainer = document.getElementById('master-forward-impact');
    if (!forward_impact.impacts || forward_impact.impacts.length === 0) {
       fwContainer.innerHTML = \`<div class="p-4 rounded bg-slate-50 border border-slate-100 text-sm text-slate-500 italic">Forward impact not available.</div>\`;
    } else {
       fwContainer.innerHTML = forward_impact.impacts.map(imp => \`
         <div class="p-3 bg-rose-50/50 border border-rose-100 rounded-lg text-sm">
           <div class="font-semibold text-rose-900 text-xs mb-1">\${escapeHtml(imp.domain)} Domain Impact</div>
           <div class="text-slate-700 leading-relaxed">\${escapeHtml(imp.impact)}</div>
           <div class="mt-2 text-[10px] font-mono text-slate-500 truncate">Target: \${escapeHtml(imp.entity_type_target)} \${escapeHtml(imp.entity_id_target)}</div>
         </div>
       \`).join('');
    }

    // Backward Impact
    const bwContainer = document.getElementById('master-backward-impact');
    if (!backward_impact.root_causes || backward_impact.root_causes.length === 0) {
       bwContainer.innerHTML = \`<div class="p-4 rounded bg-slate-50 border border-slate-100 text-sm text-slate-500 italic">Backward impact not available.</div>\`;
    } else {
       bwContainer.innerHTML = backward_impact.root_causes.map(rc => \`
         <div class="p-3 bg-amber-50/50 border border-amber-100 rounded-lg text-sm">
           <div class="font-semibold text-amber-900 text-xs mb-1">Root Cause Analysis</div>
           <div class="text-slate-700 leading-relaxed">\${escapeHtml(rc.cause)}</div>
         </div>
       \`).join('');
    }

    // Recommendations
    const recContainer = document.getElementById('master-recommendations');
    if (!recommendations || recommendations.length === 0) {
       recContainer.innerHTML = \`<div class="col-span-full p-4 rounded bg-slate-50 border border-slate-100 text-sm text-slate-500 italic">No recommendations provided.</div>\`;
    } else {
       recContainer.innerHTML = recommendations.map(rec => \`
         <div class="p-4 bg-white border border-slate-200 shadow-2xs rounded-xl flex flex-col justify-between">
           <div>
             <div class="flex items-center gap-1.5 mb-2">
               <span class="px-2 py-0.5 rounded bg-indigo-50 text-indigo-700 border border-indigo-100 text-[10px] font-bold uppercase tracking-wider">\${escapeHtml(rec.domain)}</span>
             </div>
             <div class="font-semibold text-slate-900 text-sm mb-1">\${escapeHtml(rec.action)}</div>
             <div class="text-xs text-slate-600 mb-3 leading-relaxed">\${escapeHtml(rec.reason)}</div>
           </div>
           <div class="space-y-1.5 border-t border-slate-100 pt-3">
             <div class="text-[11px]">
               <span class="font-semibold text-slate-700">Outcome:</span>
               <span class="text-slate-600">\${escapeHtml(rec.expected_outcome)}</span>
             </div>
             <div class="text-[11px]">
               <span class="font-semibold text-rose-700">Risks:</span>
               <span class="text-slate-600">\${escapeHtml(rec.key_risks)}</span>
             </div>
           </div>
         </div>
       \`).join('');
    }

    // Cross-Domain Analysis (Affected Domains)
    const affContainer = document.getElementById('master-affected-domains');
    if (affected_domains.length > 0) {
      affContainer.innerHTML = affected_domains.map(d => \`
        <span class="px-3 py-1 bg-slate-100 text-slate-700 border border-slate-200 rounded-full text-xs font-semibold">\${escapeHtml(d)}</span>
      \`).join('');
    } else {
      affContainer.innerHTML = \`<span class="text-xs text-slate-500 italic">No secondary domains affected.</span>\`;
    }

    // Target Domains Render
    const domContainer = document.getElementById('target-domains-container');
    domContainer.innerHTML = domain_results.map(res => {
      // res is typically the response from the sub-agent
      const domStatus = (res.status || 'SUCCESS').toUpperCase();
      const rec = res.recommendation || {};
      
      let title = res.domain || 'Unknown';
      let icon = 'hub';
      if (title.includes('Procurement')) icon = 'shopping_cart';
      else if (title.includes('Inventory')) icon = 'warehouse';
      else if (title.includes('Production')) icon = 'precision_manufacturing';
      else if (title.includes('Logistics')) icon = 'local_shipping';

      if (domStatus === 'ERROR' || domStatus === 'FAILED') {
          return \`
            <div class="p-4 rounded-xl bg-rose-50/40 border border-rose-200 shadow-2xs space-y-3 flex flex-col justify-between">
              <div class="flex items-center justify-between pb-2 border-b border-rose-100">
                <div class="flex items-center gap-1.5 font-semibold text-xs text-rose-950">
                  <span class="material-symbols-outlined text-[16px] text-rose-600">\${icon}</span>
                  <span>\${escapeHtml(title)}</span>
                </div>
                <span class="px-2 py-0.5 rounded text-[10px] font-medium bg-rose-100 text-rose-800 border border-rose-200">ERROR</span>
              </div>
              <p class="text-[11px] text-rose-800 leading-relaxed">\${escapeHtml(res.error_message || 'Domain analysis failed.')}</p>
            </div>
          \`;
      }

      return \`
          <div class="p-4 rounded-xl bg-white border border-slate-200 shadow-2xs space-y-3 flex flex-col justify-between">
            <div class="flex items-center justify-between pb-2 border-b border-slate-100">
              <div class="flex items-center gap-1.5 font-semibold text-xs text-slate-800">
                <span class="material-symbols-outlined text-[16px] text-indigo-600">\${icon}</span>
                <span>\${escapeHtml(title)}</span>
              </div>
              <span class="px-2 py-0.5 rounded text-[10px] font-medium bg-emerald-50 text-emerald-700 border border-emerald-200">SUCCESS</span>
            </div>
            <p class="text-[11px] text-slate-700 leading-relaxed line-clamp-3">
              \${escapeHtml(rec.action || 'No action defined')}
            </p>
          </div>
      \`;
    }).join('');

    const pipelineContainer = document.getElementById('master-pipeline-container');
    if (pipelineContainer) pipelineContainer.classList.remove('hidden');
  };
`;

const regex = /const renderMasterPipeline = \(data\) => \{[\s\S]*?\n  };\n\n  const initControlTower = async \(\) => \{/m;
js = js.replace(regex, newRenderFn + '\n\n  const initControlTower = async () => {');
fs.writeFileSync('assets/app.js', js);
console.log('Updated assets/app.js');
