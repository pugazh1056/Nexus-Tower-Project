import fs from 'fs';

let html = fs.readFileSync('control-tower.html', 'utf8');

const newButtons = `
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
`;

html = html.replace(/<button id="trigger-evt-004-btn"[\s\S]*?<\/button>/, newButtons);
fs.writeFileSync('control-tower.html', html);
console.log('Patched buttons in control-tower.html');

