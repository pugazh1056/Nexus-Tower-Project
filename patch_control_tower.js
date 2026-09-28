import fs from 'fs';

let content = fs.readFileSync('control-tower.html', 'utf8');

// Fix button container markup
const oldBtnHeader = `<div class="flex items-center gap-2">
                    <div class="flex items-center gap-2">
            <button class="trigger-evt-btn inline-flex items-center gap-1.5 px-3 py-1.5 text-[11px] font-medium text-white bg-slate-900 hover:bg-slate-800 rounded shadow-sm transition" data-evt="SUPPLIER_DELAY" type="button">
              Procurement Delay
            </button>
            <button class="trigger-evt-btn inline-flex items-center gap-1.5 px-3 py-1.5 text-[11px] font-medium text-white bg-slate-900 hover:bg-slate-800 rounded shadow-sm transition" data-evt="STOCK_LOW" type="button">
              Low Stock
            </button>
            <button class="trigger-evt-btn inline-flex items-center gap-1.5 px-3 py-1.5 text-[11px] font-medium text-white bg-slate-900 hover:bg-slate-800 rounded shadow-sm transition" data-evt="PRODUCTION_DISRUPTION" type="button">
              Production Halt
            </button>
            <button class="trigger-evt-btn inline-flex items-center gap-1.5 px-3 py-1.5 text-[11px] font-medium text-white bg-slate-900 hover:bg-slate-800 rounded shadow-sm transition" data-evt="SHIPMENT_DISRUPTION" type="button">
              Shipment Delay
            </button>
          <button id="refresh-pipeline-btn" class="inline-flex items-center gap-1.5 px-3.5 py-2 text-xs font-medium text-slate-600 bg-white border border-slate-200 rounded-lg hover:bg-slate-50 shadow-sm transition" type="button">
            <span class="material-symbols-outlined text-[16px]">refresh</span>
            Refresh
          </button>
        </div>
      </div>`;

const newBtnHeader = `<div class="flex flex-wrap items-center gap-2">
          <span class="text-xs font-semibold text-slate-500 mr-1 hidden sm:inline">Simulate Incident:</span>
          <button class="trigger-evt-btn inline-flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium text-white bg-slate-900 hover:bg-slate-800 rounded-lg shadow-sm transition" data-evt="SUPPLIER_DELAY" type="button">
            <span class="w-1.5 h-1.5 rounded-full bg-amber-400"></span> Supplier Delay
          </button>
          <button class="trigger-evt-btn inline-flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium text-white bg-slate-900 hover:bg-slate-800 rounded-lg shadow-sm transition" data-evt="STOCK_LOW" type="button">
            <span class="w-1.5 h-1.5 rounded-full bg-rose-400"></span> Low Stock
          </button>
          <button class="trigger-evt-btn inline-flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium text-white bg-slate-900 hover:bg-slate-800 rounded-lg shadow-sm transition" data-evt="PRODUCTION_DISRUPTION" type="button">
            <span class="w-1.5 h-1.5 rounded-full bg-indigo-400"></span> Production Halt
          </button>
          <button class="trigger-evt-btn inline-flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium text-white bg-slate-900 hover:bg-slate-800 rounded-lg shadow-sm transition" data-evt="SHIPMENT_DISRUPTION" type="button">
            <span class="w-1.5 h-1.5 rounded-full bg-sky-400"></span> Shipment Delay
          </button>
          <button id="refresh-pipeline-btn" class="inline-flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium text-slate-700 bg-white border border-slate-200 rounded-lg hover:bg-slate-50 shadow-sm transition" type="button">
            <span class="material-symbols-outlined text-[16px]">refresh</span>
            Refresh
          </button>
        </div>`;

content = content.replace(oldBtnHeader, newBtnHeader);

// Replace section container tag to remove `hidden` and include loading/empty/error slots
const oldSectionStart = `<section id="master-pipeline-container" class="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden transition-all hidden">`;
const newSectionStart = `<section id="master-pipeline-container" class="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden transition-all">
        <!-- Loading State -->
        <div id="pipeline-loading" class="p-12 text-center space-y-3 hidden">
          <div class="inline-flex items-center justify-center w-12 h-12 rounded-full bg-indigo-50 text-indigo-600 mb-2">
            <span class="material-symbols-outlined text-[24px] animate-spin">sync</span>
          </div>
          <h3 class="text-sm font-semibold text-slate-900">Executing Master Agent Intelligence Pipeline...</h3>
          <p class="text-xs text-slate-500 max-w-md mx-auto">Evaluating cross-domain impact matrix across Procurement, Inventory, Production, and Logistics.</p>
        </div>

        <!-- Empty State -->
        <div id="pipeline-empty" class="p-12 text-center space-y-3 hidden">
          <div class="inline-flex items-center justify-center w-12 h-12 rounded-full bg-slate-100 text-slate-400 mb-2">
            <span class="material-symbols-outlined text-[24px]">hub</span>
          </div>
          <h3 class="text-sm font-semibold text-slate-900">No Active Master Orchestrator Events</h3>
          <p class="text-xs text-slate-500 max-w-md mx-auto">Click one of the incident triggers above to simulate supply chain disruption analysis.</p>
        </div>

        <!-- Error State -->
        <div id="pipeline-error" class="p-8 text-center space-y-3 hidden">
          <div class="inline-flex items-center justify-center w-12 h-12 rounded-full bg-rose-50 text-rose-600 mb-2">
            <span class="material-symbols-outlined text-[24px]">warning</span>
          </div>
          <h3 class="text-sm font-semibold text-slate-900">Master Orchestrator Connection Error</h3>
          <p id="pipeline-error-detail" class="text-xs text-rose-600 max-w-md mx-auto font-mono bg-rose-50 p-2 rounded border border-rose-100">Unable to retrieve master response.</p>
          <button id="pipeline-retry-btn" class="mt-2 inline-flex items-center gap-1.5 px-4 py-2 text-xs font-medium text-white bg-slate-900 hover:bg-slate-800 rounded-lg transition" type="button">
            <span class="material-symbols-outlined text-[16px]">refresh</span> Retry Pipeline
          </button>
        </div>`;

content = content.replace(oldSectionStart, newSectionStart);

fs.writeFileSync('control-tower.html', content);
console.log('Control Tower HTML patched successfully');
