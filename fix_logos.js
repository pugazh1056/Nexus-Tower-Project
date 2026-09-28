import fs from 'fs';
const files = ['control-tower.html', 'procurement.html', 'inventory.html', 'production.html', 'logistics.html'];

files.forEach(file => {
  if (fs.existsSync(file)) {
    let content = fs.readFileSync(file, 'utf8');
    content = content.replace(
      /<div class="h-16 px-6 flex items-center gap-3 border-b border-border-subtle">[\s\S]*?<\/div>\s*<\/div>\s*<nav/m,
      `<a href="index.html" class="h-16 px-6 flex items-center gap-3 border-b border-border-subtle hover:bg-slate-50 transition-colors">
        <div class="w-8 h-8 rounded-lg bg-slate-900 text-white flex items-center justify-center shadow-sm shrink-0">
          <span class="material-symbols-outlined text-[18px]">deployed_code</span>
        </div>
        <div class="flex flex-col">
          <div class="flex items-center gap-1">
            <span class="font-display text-[15px] leading-snug tracking-tight font-bold text-slate-900">NEXUS</span>
            <span class="font-display text-[15px] leading-snug tracking-tight font-semibold text-indigo-700">TOWER</span>
          </div>
          <span class="text-[10px] text-slate-500 font-mono tracking-wide uppercase leading-none mt-0.5">Operations Cockpit</span>
        </div>
      </a>
      <nav`
    );
    fs.writeFileSync(file, content);
    console.log(`Updated ${file}`);
  }
});
