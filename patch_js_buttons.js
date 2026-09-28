import fs from 'fs';

let js = fs.readFileSync('assets/app.js', 'utf8');

const oldBinding = `    const triggerEvtBtn = document.getElementById('trigger-evt-004-btn');
    if (triggerEvtBtn) {
      triggerEvtBtn.addEventListener('click', async () => {
        showLoading();
        try {
          const res = await window.NexusAPI.triggerMasterTestEvent('EVT-TEST-004');
          if (!res || (typeof res === 'object' && Object.keys(res).length === 0)) {
            showEmpty();
          } else {
            renderMasterPipeline(res);
            showContent();
            window.NexusAPI.showToast('Master response received for EVT-TEST-004', 'success');
          }
        } catch (err) {
          showError(err);
        }
      });
    }`;

const newBinding = `    const triggerBtns = document.querySelectorAll('.trigger-evt-btn');
    triggerBtns.forEach(btn => {
      btn.addEventListener('click', async (e) => {
        const evtId = e.currentTarget.dataset.evt;
        showLoading();
        try {
          const res = await window.NexusAPI.triggerMasterTestEvent(evtId);
          if (!res || (typeof res === 'object' && Object.keys(res).length === 0)) {
            showEmpty();
          } else {
            renderMasterPipeline(res);
            showContent();
            window.NexusAPI.showToast(\`Master response received for \${evtId}\`, 'success');
          }
        } catch (err) {
          showError(err);
        }
      });
    });`;

if (js.includes('trigger-evt-004-btn')) {
    js = js.replace(oldBinding, newBinding);
    fs.writeFileSync('assets/app.js', js);
    console.log('Patched JS button binding');
} else {
    console.log('Could not find old binding, using regex.');
    const regex = /const triggerEvtBtn = document\.getElementById\('trigger-evt-004-btn'\);[\s\S]*?\}\);[\s\S]*?\}/;
    js = js.replace(regex, newBinding);
    fs.writeFileSync('assets/app.js', js);
    console.log('Patched JS button binding using regex');
}

