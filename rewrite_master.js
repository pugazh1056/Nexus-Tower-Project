import fs from 'fs';

// 1. Rewrite control-tower.html
let html = fs.readFileSync('control-tower.html', 'utf8');

const newContainer = `
      <section id="master-pipeline-container" class="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden transition-all hidden">
        <!-- Pipeline Header Bar -->
        <div class="p-5 sm:p-6 bg-slate-900 text-white flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div class="space-y-1">
            <div class="flex flex-wrap items-center gap-2.5">
              <span class="px-2.5 py-0.5 rounded bg-indigo-500/20 text-indigo-300 text-xs font-semibold tracking-wide border border-indigo-400/30 uppercase">Master Orchestrator</span>
              <span id="pipeline-status-badge" class="px-2.5 py-0.5 rounded bg-emerald-500/20 text-emerald-300 text-xs font-medium border border-emerald-400/30"></span>
            </div>
            <div class="flex flex-wrap items-baseline gap-3 pt-1">
              <span class="text-base sm:text-lg font-semibold text-white tracking-tight">Event: <span id="pipeline-event-id" class="text-indigo-300 text-sm sm:text-base font-semibold"></span></span>
              <span class="text-slate-400 text-xs">• Pipeline ID: <span id="pipeline-exec-id" class="text-slate-200 font-mono text-[10px]"></span></span>
            </div>
          </div>
          <div class="flex items-center gap-4 text-right">
             <div>
                <div class="text-[10px] text-slate-400 uppercase font-medium">Source Domain</div>
                <div id="pipeline-source-domain" class="text-sm font-semibold text-white"></div>
             </div>
             <div class="h-8 w-px bg-slate-700 hidden sm:block"></div>
             <div>
                <div class="text-[10px] text-slate-400 uppercase font-medium">Primary Domain</div>
                <div id="pipeline-primary-domain" class="text-sm font-semibold text-indigo-300"></div>
             </div>
             <div class="h-8 w-px bg-slate-700 hidden sm:block"></div>
             <div>
                <div class="text-[10px] text-slate-400 uppercase font-medium">Approval</div>
                <div id="pipeline-approval-status" class="text-sm font-bold text-amber-300 font-mono"></div>
             </div>
          </div>
        </div>

        <div id="pipeline-body" class="p-6 space-y-6">
          
          <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <!-- Forward Impact -->
            <div class="space-y-3">
              <div class="flex items-center gap-2 pb-2 border-b border-slate-100">
                 <span class="material-symbols-outlined text-[18px] text-rose-600">trending_flat</span>
                 <h3 class="text-xs font-bold uppercase tracking-wider text-slate-800">Forward Impact (Downstream)</h3>
              </div>
              <div id="master-forward-impact" class="space-y-3"></div>
            </div>

            <!-- Backward Impact -->
            <div class="space-y-3">
              <div class="flex items-center gap-2 pb-2 border-b border-slate-100">
                 <span class="material-symbols-outlined text-[18px] text-amber-600">history</span>
                 <h3 class="text-xs font-bold uppercase tracking-wider text-slate-800">Backward Impact (Root Cause)</h3>
              </div>
              <div id="master-backward-impact" class="space-y-3"></div>
            </div>
          </div>

          <!-- Recommendations -->
          <div class="space-y-3 pt-4 border-t border-slate-100">
            <div class="flex items-center justify-between pb-2 border-b border-slate-100">
              <div class="flex items-center gap-2">
                 <span class="material-symbols-outlined text-[18px] text-indigo-600">psychology</span>
                 <h3 class="text-xs font-bold uppercase tracking-wider text-slate-800">Prescriptive Recommendations</h3>
              </div>
            </div>
            <div id="master-recommendations" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4"></div>
          </div>

          <!-- Cross-Domain Analysis -->
          <div class="space-y-3 pt-4 border-t border-slate-100">
            <div class="flex items-center gap-2 pb-2 border-b border-slate-100">
               <span class="material-symbols-outlined text-[18px] text-slate-700">hub</span>
               <h3 class="text-xs font-bold uppercase tracking-wider text-slate-800">Cross-Domain Evaluated Agents</h3>
            </div>
            <div id="master-affected-domains" class="flex flex-wrap gap-2"></div>
            <div id="target-domains-container" class="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-4 mt-3"></div>
          </div>

        </div>
      </section>
`;

html = html.replace(/<section id="master-pipeline-container"[\s\S]*?<\/section>/, newContainer);
fs.writeFileSync('control-tower.html', html);
console.log('Updated control-tower.html');

