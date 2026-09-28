import fs from 'fs';
let js = fs.readFileSync('assets/app.js', 'utf8');

const regex = /bwContainer\.innerHTML = backward_impact\.root_causes\.map\(rc => `[\s\S]*?`\)\.join\(''\);/;

const newBw = `bwContainer.innerHTML = backward_impact.root_causes.map(rc => \`
         <div class="p-3 bg-amber-50/50 border border-amber-100 rounded-lg text-sm">
           <div class="font-semibold text-amber-900 text-xs mb-1">\${escapeHtml(rc.domain)} Domain Root Cause</div>
           <div class="text-slate-700 leading-relaxed">\${escapeHtml(rc.cause)}</div>
           <div class="mt-2 text-[10px] font-mono text-slate-500 truncate">Target: \${escapeHtml(rc.entity_type_target)} \${escapeHtml(rc.entity_id_target)}</div>
         </div>
       \`).join('');`;

js = js.replace(regex, newBw);
fs.writeFileSync('assets/app.js', js);
console.log('patched bw impact');
