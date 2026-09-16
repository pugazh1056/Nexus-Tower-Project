/**
 * Nexus Tower - Core Frontend Application Controller
 * Integrates static UI layouts with real backend APIs and handles role-based UI gating.
 */

(() => {
  'use strict';

  const page = document.body.dataset.page || 'home';

  const pages = {
    login: 'login.html',
    controlTower: 'control-tower.html',
    procurement: 'procurement.html',
    inventory: 'inventory.html',
    production: 'production.html',
    logistics: 'logistics.html',
  };

  const roleTargets = {
    Procurement: {
      email: 'm.vance@nexustower.internal',
      tag: 'ROLE: PROC-MG',
      title: 'Procurement Lead',
      href: pages.procurement,
      pageKey: 'procurement',
      role: 'procurement',
    },
    Inventory: {
      email: 's.chen@nexustower.internal',
      tag: 'ROLE: INVT-LEAD',
      title: 'Inventory Lead',
      href: pages.inventory,
      pageKey: 'inventory',
      role: 'inventory',
    },
    Production: {
      email: 'k.novak@nexustower.internal',
      tag: 'ROLE: PROD-DIR',
      title: 'Production Lead',
      href: pages.production,
      pageKey: 'production',
      role: 'production',
    },
    Logistics: {
      email: 'd.morales@nexustower.internal',
      tag: 'ROLE: LOGS-SPEC',
      title: 'Logistics Lead',
      href: pages.logistics,
      pageKey: 'logistics',
      role: 'logistics',
    },
    'Control Tower': {
      email: 'ops-admin@nexustower.internal',
      tag: 'ROLE: TOWER-ROOT',
      title: 'Operations Director',
      href: pages.controlTower,
      pageKey: 'controlTower',
      role: 'admin',
    },
  };

  const pageRoleMap = {
    controlTower: 'controlTower',
    procurement: 'procurement',
    inventory: 'inventory',
    production: 'production',
    logistics: 'logistics',
  };

  const setActiveNav = (currentPage) => {
    document.querySelectorAll('[data-nav]').forEach((link) => {
      const active = link.dataset.nav === currentPage;
      link.classList.toggle('bg-slate-900', active);
      link.classList.toggle('text-white', active);
      link.classList.toggle('shadow-sm', active);
      link.classList.toggle('text-slate-600', !active);
      link.classList.toggle('hover:bg-slate-50', !active);
      link.querySelectorAll('[data-nav-icon]').forEach((icon) => {
        icon.classList.toggle('text-white', active);
        icon.classList.toggle('text-slate-400', !active);
      });
    });
  };

  const bindThemeToggle = () => {
    const themeBtn = document.getElementById('theme-toggle');
    const themeIcon = document.getElementById('theme-icon');
    if (!themeBtn || !themeIcon) return;

    const applyState = () => {
      const isDark = document.documentElement.classList.contains('dark');
      themeIcon.textContent = isDark ? 'light_mode' : 'dark_mode';
      window.localStorage.setItem('nexus-theme', isDark ? 'dark' : 'light');
    };

    themeBtn.addEventListener('click', () => {
      document.documentElement.classList.toggle('dark');
      applyState();
    });

    applyState();
  };

  const bindUserHeader = () => {
    if (!window.NexusAPI) return;
    const user = window.NexusAPI.getCurrentUser();
    if (!user) return;

    // Update user name in header
    document.querySelectorAll('header .text-on-surface, header .text-slate-800').forEach((el) => {
      if (el.textContent && (el.textContent.includes('Marcus Vance') || el.textContent.includes('Lead') || el.textContent.includes('Admin'))) {
        el.textContent = user.full_name || 'Operations Lead';
      }
    });

    // Update role badge in header
    const roleBadge = document.querySelector('header .bg-slate-100');
    if (roleBadge && user.role) {
      const roleLabelMap = {
        admin: 'Control Tower Director',
        procurement: 'Procurement Manager',
        inventory: 'Inventory Manager',
        production: 'Production Manager',
        logistics: 'Logistics Manager',
      };
      roleBadge.textContent = roleLabelMap[user.role] || `${user.role.toUpperCase()} Manager`;
    }
  };

  const bindLogin = () => {
    const form = document.getElementById('auth-form');
    if (!form) return;

    const personaButtons = Array.from(document.querySelectorAll('.persona-btn'));
    const roleTag = document.getElementById('role-tag');
    const emailInput = document.getElementById('work-email');
    const passwordInput = document.getElementById('password');
    const togglePassword = document.getElementById('toggle-pwd');
    const passwordIcon = document.getElementById('pwd-icon');
    const loginButton = document.getElementById('submit-btn');

    // Check for session expired param
    const urlParams = new URLSearchParams(window.location.search);
    if (urlParams.get('expired')) {
      const notice = document.createElement('div');
      notice.className = 'mb-4 p-3 bg-amber-50 border border-amber-200 text-amber-800 text-xs rounded-xl flex items-center gap-2';
      notice.innerHTML = '<span class="material-symbols-outlined text-[16px]">info</span><span>Your session has expired. Please sign in again.</span>';
      form.prepend(notice);
    }

    const setPersona = (roleName) => {
      personaButtons.forEach((button) => {
        const active = button.dataset.role === roleName;
        button.classList.toggle('bg-surface-container-lowest', active);
        button.classList.toggle('text-on-surface', active);
        button.classList.toggle('shadow-sm', active);
        button.classList.toggle('font-semibold', active);
        button.classList.toggle('text-on-surface-variant', !active);
      });

      const role = roleTargets[roleName];
      if (!role) return;

      if (emailInput) emailInput.value = role.email;
      if (passwordInput) passwordInput.value = 'password123';
      if (roleTag) roleTag.textContent = role.tag;
      if (loginButton) {
        loginButton.dataset.target = role.href;
        loginButton.dataset.role = roleName;
      }
    };

    personaButtons.forEach((button) => {
      button.addEventListener('click', () => setPersona(button.dataset.role));
    });

    if (togglePassword && passwordInput && passwordIcon) {
      togglePassword.addEventListener('click', () => {
        const reveal = passwordInput.type === 'password';
        passwordInput.type = reveal ? 'text' : 'password';
        passwordIcon.textContent = reveal ? 'visibility_off' : 'visibility';
      });
    }

    // Default to Procurement
    setPersona('Procurement');

    form.addEventListener('submit', async (event) => {
      event.preventDefault();
      const email = emailInput?.value?.trim() || 'm.vance@nexustower.internal';
      const password = passwordInput?.value || 'password123';

      // Clear previous errors
      const prevError = document.getElementById('login-error-msg');
      if (prevError) prevError.remove();

      // Show loading state
      const origButtonHtml = loginButton.innerHTML;
      loginButton.disabled = true;
      loginButton.innerHTML = `
        <span class="inline-block animate-spin material-symbols-outlined text-[18px]">sync</span>
        <span>Authenticating...</span>
      `;

      try {
        if (window.NexusAPI) {
          const authResult = await window.NexusAPI.login(email, password);
          const userRole = authResult.user?.role || 'procurement';
          const rolePageMap = {
            admin: pages.controlTower,
            procurement: pages.procurement,
            inventory: pages.inventory,
            production: pages.production,
            logistics: pages.logistics,
          };
          const target = rolePageMap[userRole] || loginButton.dataset.target || pages.controlTower;
          window.location.href = target;
        } else {
          // Fallback if API not loaded
          const roleName = loginButton?.dataset.role || 'Procurement';
          const target = loginButton?.dataset.target || pages.controlTower;
          sessionStorage.setItem('nexus-role', roleName);
          sessionStorage.setItem('nexus-role-page', roleTargets[roleName]?.pageKey || 'controlTower');
          window.location.href = target;
        }
      } catch (err) {
        loginButton.disabled = false;
        loginButton.innerHTML = origButtonHtml;

        const errorDiv = document.createElement('div');
        errorDiv.id = 'login-error-msg';
        errorDiv.className = 'mt-3 p-3 bg-rose-50 border border-rose-200 text-rose-700 text-xs rounded-xl flex items-center gap-2';
        errorDiv.innerHTML = `
          <span class="material-symbols-outlined text-[16px]">error</span>
          <span>${err.message || 'Authentication failed. Please verify credentials.'}</span>
        `;
        form.appendChild(errorDiv);
      }
    });
  };

  const bindLogout = () => {
    const logoutBtn = document.getElementById('logout-btn');
    if (!logoutBtn) return;

    logoutBtn.addEventListener('click', async () => {
      if (window.NexusAPI) {
        await window.NexusAPI.logout();
      } else {
        sessionStorage.removeItem('nexus-role');
        sessionStorage.removeItem('nexus-role-page');
        window.location.href = pages.login;
      }
    });
  };

  const enforceAccessControl = () => {
    if (page === 'login' || page === 'home') return;

    const token = window.NexusAPI ? window.NexusAPI.getToken() : null;
    const storedRole = sessionStorage.getItem('nexus-role');
    const storedRolePage = sessionStorage.getItem('nexus-role-page');

    if (!token && (!storedRole || !storedRolePage)) {
      window.location.href = pages.login;
      return;
    }

    const isControlTower = storedRolePage === 'controlTower' || storedRole === 'admin' || storedRole === 'Control Tower';

    // For non-Control-Tower roles, enforce page restriction
    if (!isControlTower && pageRoleMap[page] !== storedRolePage) {
      const targetHref = pages[storedRolePage] || pages.login;
      window.location.href = targetHref;
      return;
    }

    // Remove the sidebar navigation for non-Control-Tower roles
    if (!isControlTower) {
      const sidebar = document.querySelector('aside');
      if (sidebar) {
        sidebar.remove();
      }

      const contentWrapper = document.querySelector('.lg\\:pl-64');
      if (contentWrapper) {
        contentWrapper.classList.remove('lg:pl-64');
      }
    }
  };

  const bindDismissableCards = () => {
    document.querySelectorAll('[data-dismiss-target]').forEach((button) => {
      button.addEventListener('click', () => {
        const target = document.getElementById(button.dataset.dismissTarget);
        if (target) target.remove();
      });
    });
  };

  // =========================================================================
  // PAGE-SPECIFIC REAL DATA INITIALIZERS
  // =========================================================================

  // =========================================================================
  // MASTER INTELLIGENCE PIPELINE CONTROLLER
  // =========================================================================

  const renderMasterPipeline = (data) => {
    if (!data) return;

    // Execution & Event Info
    const execIdEl = document.getElementById('pipeline-execution-id');
    const eventIdEl = document.getElementById('pipeline-event-id');
    const statusBadgeEl = document.getElementById('pipeline-status-badge');
    const timeBadgeEl = document.getElementById('pipeline-time-badge');
    const urgencyScoreEl = document.getElementById('pipeline-urgency-score');
    const severityBadgeEl = document.getElementById('pipeline-severity-badge');

    if (execIdEl) execIdEl.textContent = data.pipeline_execution_id || 'EXEC-MST-LIVE';
    if (eventIdEl) eventIdEl.textContent = data.event_id || 'EVT-TEST-004';
    if (statusBadgeEl) statusBadgeEl.textContent = `STATUS: ${data.status || 'COMPLETED'}`;
    if (timeBadgeEl) timeBadgeEl.textContent = data.timestamp || new Date().toISOString();

    const stages = data.stages || {};

    // 1. Normalization Stage
    const norm = stages.normalization || {};
    const normSource = document.getElementById('norm-source');
    const normType = document.getElementById('norm-type');
    const normEntity = document.getElementById('norm-entity');
    const normSupplier = document.getElementById('norm-supplier');
    const normDelay = document.getElementById('norm-delay');

    if (normSource) normSource.textContent = norm.source_domain || 'Procurement Agent';
    if (normType) normType.textContent = norm.event_type || 'SUPPLIER_DELAY';
    if (normEntity) {
      const prodName = norm.product?.name ? ` (${norm.product.name})` : '';
      normEntity.textContent = `${norm.entity_id || 'PO-001'}${prodName}`;
    }
    if (normSupplier) {
      const supCode = norm.supplier?.supplier_code ? ` (${norm.supplier.supplier_code})` : '';
      normSupplier.textContent = `${norm.supplier?.name || 'Dairy Pure Co'}${supCode}`;
    }
    if (normDelay) {
      const delayDays = norm.delay_parameters?.delay_days ?? 8;
      const origDate = norm.delay_parameters?.original_expected_date || '2026-09-06';
      const revDate = norm.delay_parameters?.revised_expected_date || '2026-09-14';
      normDelay.textContent = `+${delayDays} Days (${origDate} → ${revDate})`;
    }

    // 2. Dynamic Priority Stage
    const prio = stages.priority || {};
    const prioSlaBadge = document.getElementById('prio-sla-badge');
    const prioJustification = document.getElementById('prio-justification');
    const prioUrgency = document.getElementById('prio-urgency');

    if (urgencyScoreEl) {
      urgencyScoreEl.innerHTML = `${prio.urgency_score ?? 92.4} <span class="text-xs text-slate-400 font-normal">/ 100</span>`;
    }
    if (severityBadgeEl && prio.severity) {
      severityBadgeEl.innerHTML = `<span class="w-1.5 h-1.5 rounded-full bg-rose-400"></span> ${prio.severity}`;
    }
    if (prioSlaBadge) prioSlaBadge.textContent = prio.sla_impact ? prio.sla_impact.replace('_', ' ') : 'BREACH IMMINENT';
    if (prioJustification) prioJustification.textContent = prio.justification || '8-day delay on primary feedstock with single-silo buffer below 38h threshold.';
    if (prioUrgency) prioUrgency.textContent = `${prio.urgency_score ?? 92.4} / 100`;

    // 3. Backward Impact Stage
    const back = stages.backward_impact || {};
    const backCause = document.getElementById('back-cause');
    const backOtd = document.getElementById('back-otd');
    const backContract = document.getElementById('back-contract');
    const backPenalty = document.getElementById('back-penalty');

    if (backCause) backCause.textContent = back.root_cause || 'Refrigeration compressor breakdown during pre-transit';
    if (backOtd && back.historical_supplier_performance) {
      const otdRate = Math.round((back.historical_supplier_performance.on_time_delivery_rate || 0.75) * 100);
      const orders = back.historical_supplier_performance.total_historical_orders || 4;
      backOtd.textContent = `${otdRate}.0% (${orders} POs)`;
    }
    if (backContract && back.contract_audit) {
      const slaMin = Math.round((back.contract_audit.sla_minimum || 0.95) * 100);
      backContract.textContent = `${back.contract_audit.contract_id || 'CTR-SUP001-2026'} (${slaMin}% SLA)`;
    }
    if (backPenalty && back.contract_audit) {
      const penalty = back.contract_audit.applicable_penalty_amount || 800;
      backPenalty.textContent = `$${Number(penalty).toFixed(2)} applicable`;
    }

    // 4. Forward Impact Stage
    const fwd = stages.forward_impact || {};
    const fwdDomains = document.getElementById('forward-affected-domains');
    if (fwdDomains && fwd.affected_domains) {
      fwdDomains.innerHTML = fwd.affected_domains
        .map((d) => `<span class="px-2 py-0.5 rounded bg-indigo-100 text-indigo-800 text-[11px] font-mono font-medium">${d}</span>`)
        .join('');
    }

    const fwdInvQty = document.getElementById('fwd-inv-qty');
    const fwdInvRunway = document.getElementById('fwd-inv-runway');
    if (fwdInvQty && fwd.inventory_impact) {
      fwdInvQty.textContent = `${fwd.inventory_impact.current_available_quantity ?? 30.0} L (Deficit ${fwd.inventory_impact.deficit ?? 70.0} L)`;
    }
    if (fwdInvRunway && fwd.inventory_impact) {
      fwdInvRunway.textContent = `${fwd.inventory_impact.runway_hours ?? 28.8} Hours`;
    }

    const fwdProdShortage = document.getElementById('fwd-prod-shortage');
    const fwdProdHazard = document.getElementById('fwd-prod-hazard');
    if (fwdProdShortage && fwd.production_impact) {
      fwdProdShortage.textContent = `${fwd.production_impact.material_shortage ?? 795.0} / ${fwd.production_impact.feedstock_required ?? 840.0} L`;
    }
    if (fwdProdHazard && fwd.production_impact) {
      fwdProdHazard.textContent = (fwd.production_impact.starvation_hazard || 'CRITICAL IDLE RISK').replace(/_/g, ' ');
    }

    const fwdLogsRev = document.getElementById('fwd-logs-revenue');
    const fwdLogsOtif = document.getElementById('fwd-logs-otif');
    if (fwdLogsRev && fwd.logistics_fulfillment_impact) {
      fwdLogsRev.textContent = `$${Number(fwd.logistics_fulfillment_impact.estimated_revenue_at_risk || 14200).toLocaleString()}.00`;
    }
    if (fwdLogsOtif && fwd.logistics_fulfillment_impact) {
      const otif = Math.round((fwd.logistics_fulfillment_impact.fill_rate_projection_without_action || 0.42) * 100);
      fwdLogsOtif.textContent = `${otif}.0%`;
    }

    // 5. Demand Forecasting Gate Stage
    const dem = stages.demand_forecasting_gate || {};
    const demStatus = document.getElementById('demand-gate-status');
    const demSku = document.getElementById('demand-sku');
    const demBurn = document.getElementById('demand-burn');
    const dem7d = document.getElementById('demand-7d');
    const dem14d = document.getElementById('demand-14d');
    const demSafety = document.getElementById('demand-safety');
    const demDecisionGate = document.getElementById('demand-decision-gate');

    if (demStatus) demStatus.textContent = dem.gate_status ? dem.gate_status.replace(/_/g, ' ') : 'BREACHED';
    if (demSku) demSku.textContent = dem.sku || 'MILK-001';
    if (demBurn) demBurn.textContent = `${dem.daily_consumption_rate ?? 25.0} L / day`;
    if (dem7d) dem7d.textContent = `${dem.projected_7_day_demand ?? 175.0} L`;
    if (dem14d) dem14d.textContent = `${dem.projected_14_day_demand ?? 350.0} L`;
    if (demSafety) demSafety.textContent = `${dem.safety_stock_threshold ?? 100.0} L`;
    if (demDecisionGate) demDecisionGate.textContent = dem.decision_gate || 'PASSED_TO_OPTIMIZER';

    // 6. Decision Optimization Stage
    const opt = stages.decision_optimization || {};
    const optTbody = document.getElementById('opt-options-tbody');
    if (optTbody && opt.evaluated_options) {
      optTbody.innerHTML = opt.evaluated_options
        .map((o) => {
          const isSelected = o.strategy === opt.selected_recommendation?.action_strategy || o.score > 90;
          const netPositive = o.net_financial_impact >= 0;
          const netFormatted = netPositive
            ? `+$${Number(o.net_financial_impact).toLocaleString()}`
            : `-$${Number(Math.abs(o.net_financial_impact)).toLocaleString()}`;

          return `
            <tr class="hover:bg-slate-100/60 transition ${isSelected ? 'bg-indigo-50/50 font-semibold text-indigo-950' : 'text-slate-600'}">
              <td class="py-2.5 pr-3">
                <div class="flex items-center gap-1.5">
                  ${isSelected ? '<span class="material-symbols-outlined text-[14px] text-indigo-600">check_circle</span>' : '<span class="w-2 h-2 rounded-full bg-slate-300"></span>'}
                  <span>${o.strategy.replace(/_/g, ' ')}</span>
                </div>
              </td>
              <td class="py-2.5 px-3 text-right text-slate-700">$${Number(o.cost).toLocaleString()}</td>
              <td class="py-2.5 px-3 text-right text-slate-700">$${Number(o.production_downtime_loss).toLocaleString()}</td>
              <td class="py-2.5 px-3 text-right ${netPositive ? 'text-emerald-700 font-bold' : 'text-rose-600'}">${netFormatted}</td>
              <td class="py-2.5 px-3 text-right">${Math.round(o.otif_projection * 100)}%</td>
              <td class="py-2.5 pl-3 text-right ${isSelected ? 'text-indigo-700 font-bold' : 'text-slate-500'}">${o.score}</td>
            </tr>
          `;
        })
        .join('');
    }

    const selRec = opt.selected_recommendation || {};
    const recTitle = document.getElementById('rec-title');
    const recDesc = document.getElementById('rec-desc');
    const recConf = document.getElementById('rec-confidence');
    const recProtected = document.getElementById('rec-protected-val');

    if (recTitle && selRec.title) recTitle.textContent = selRec.title;
    if (recDesc && selRec.description) recDesc.textContent = selRec.description;
    if (recConf && selRec.confidence_score) recConf.textContent = `${(selRec.confidence_score * 100).toFixed(1)}% Confidence`;
    if (recProtected && selRec.net_protected_value) {
      recProtected.textContent = `+$${Number(selRec.net_protected_value).toLocaleString()} Net Protected`;
    }

    // 7. Smart Replenishment Stage
    const rep = stages.smart_replenishment || {};
    const repStatusBadge = document.getElementById('replenishment-status-badge');
    const repSupplier = document.getElementById('rep-supplier');
    const repItem = document.getElementById('rep-item');
    const repQty = document.getElementById('rep-qty');
    const repTotal = document.getElementById('rep-total');
    const repUnitPrice = document.getElementById('rep-unit-price');
    const repEta = document.getElementById('rep-eta');
    const repReqId = document.getElementById('rep-req-id');

    if (repStatusBadge) repStatusBadge.textContent = rep.status || 'PROPOSED_PENDING_APPROVAL';
    if (repSupplier && rep.supplier) {
      repSupplier.textContent = `${rep.supplier.name || 'Apex Dairy Farms'} (${rep.supplier.supplier_code || 'SUP-005'})`;
    }
    if (repItem && rep.replenishment_item) {
      repItem.textContent = rep.replenishment_item.name || 'Raw Pasteurization Feedstock';
    }
    if (repQty && rep.replenishment_item) {
      repQty.textContent = `${rep.replenishment_item.quantity} ${rep.replenishment_item.unit} (${rep.replenishment_item.sku || 'RAW-MILK-01'})`;
    }
    if (repTotal && rep.replenishment_item) {
      repTotal.textContent = `$${Number(rep.replenishment_item.total_amount || 29600).toLocaleString()}.00 ${rep.replenishment_item.currency || 'USD'}`;
    }
    if (repUnitPrice && rep.replenishment_item) {
      repUnitPrice.textContent = `$${Number(rep.replenishment_item.unit_price || 37).toFixed(2)} / ${rep.replenishment_item.unit || 'unit'}`;
    }
    if (repEta) repEta.textContent = rep.estimated_delivery_date || '2026-09-18';
    if (repReqId) repReqId.textContent = rep.requisition_id || 'REQ-AUTO-2026-004';

    // 8. Execution Boundary & Proposed Executable Actions Stage
    const exec = stages.execution_boundary || {};
    const execRoles = document.getElementById('exec-roles');
    const execAppStatus = document.getElementById('exec-approval-status');
    const actionsContainer = document.getElementById('proposed-actions-container');

    if (execRoles && exec.authorized_roles) {
      execRoles.textContent = exec.authorized_roles.join(', ');
    }
    if (execAppStatus) {
      execAppStatus.textContent = exec.status || 'AWAITING_AUTHORIZATION';
    }

    if (actionsContainer && exec.executable_actions) {
      actionsContainer.innerHTML = exec.executable_actions
        .map((act, idx) => {
          const isPo = act.action_type === 'CREATE_PURCHASE_ORDER';
          const icon = isPo ? 'shopping_bag' : 'notifications_active';
          const detail = isPo
            ? `Emergency Purchase Order: ${act.payload?.po_number || 'PO-EMERGENCY-001'} (800L @ $37.00 via Apex Dairy Farms)`
            : `Domain Broadcast: ${act.payload?.title || 'Raw Milk Feedstock Expedite Dispatched'}`;

          return `
            <div class="p-3.5 rounded-lg bg-slate-800/80 border border-slate-700 space-y-2">
              <div class="flex items-center justify-between">
                <div class="flex items-center gap-2">
                  <span class="material-symbols-outlined text-[16px] text-amber-400">${icon}</span>
                  <span class="text-xs font-mono font-semibold text-white">${act.action_type}</span>
                </div>
                <span class="px-2 py-0.5 rounded text-[10px] font-mono bg-amber-500/20 text-amber-300 border border-amber-400/20">PROPOSED ACTION</span>
              </div>
              <p class="text-xs text-slate-300">${detail}</p>
              <div class="flex items-center justify-between text-[11px] font-mono text-slate-400 pt-1 border-t border-slate-700/60">
                <span>Target: <strong class="text-slate-200">${act.method || 'POST'} ${act.endpoint || '/api/'}</strong></span>
                <span class="text-amber-400">Requires Auth</span>
              </div>
            </div>
          `;
        })
        .join('');
    }

    // Bind Action Review Modal
    const modalBtn = document.getElementById('review-action-modal-btn');
    const modal = document.getElementById('action-modal');
    const modalContent = document.getElementById('modal-json-content');
    const closeModalBtn = document.getElementById('close-modal-btn');
    const modalCancelBtn = document.getElementById('modal-cancel-btn');
    const modalConfirmBtn = document.getElementById('modal-confirm-btn');

    if (modalBtn && modal && modalContent) {
      modalBtn.onclick = () => {
        modalContent.textContent = JSON.stringify(exec, null, 2);
        modal.classList.remove('hidden');
      };
    }

    const closeModal = () => {
      if (modal) modal.classList.add('hidden');
    };

    if (closeModalBtn) closeModalBtn.onclick = closeModal;
    if (modalCancelBtn) modalCancelBtn.onclick = closeModal;
    if (modalConfirmBtn) {
      modalConfirmBtn.onclick = () => {
        closeModal();
        window.NexusAPI.showToast('Human Governance: Actions acknowledged as proposed.', 'info');
      };
    }

    // Authorize button: Updates review UI safely without triggering unauthorized execution
    const authorizeBtn = document.getElementById('authorize-master-action-btn');
    if (authorizeBtn) {
      authorizeBtn.onclick = () => {
        authorizeBtn.disabled = true;
        authorizeBtn.innerHTML = '<span class="material-symbols-outlined text-[16px]">check_circle</span><span>Authorized by Human Lead</span>';
        authorizeBtn.className = 'w-full sm:w-auto px-5 py-2 rounded-lg bg-emerald-600 text-white text-xs font-medium shadow-sm transition flex items-center justify-center gap-1.5';
        if (execAppStatus) {
          execAppStatus.textContent = 'AUTHORIZED_BY_HUMAN';
          execAppStatus.className = 'text-emerald-400 font-mono';
        }
        window.NexusAPI.showToast('Master proposed actions authorized by Supply Chain Lead!', 'success');
      };
    }
  };

  const initControlTower = async () => {
    if (!window.NexusAPI) return;

    const pipelineLoading = document.getElementById('pipeline-loading');
    const pipelineBody = document.getElementById('pipeline-body');
    const pipelineError = document.getElementById('pipeline-error');
    const pipelineErrorDetail = document.getElementById('pipeline-error-detail');
    const connectionBadge = document.getElementById('master-connection-badge');

    const showLoading = () => {
      if (pipelineLoading) pipelineLoading.classList.remove('hidden');
      if (pipelineBody) pipelineBody.classList.add('hidden');
      if (pipelineError) pipelineError.classList.add('hidden');
    };

    const showContent = () => {
      if (pipelineLoading) pipelineLoading.classList.add('hidden');
      if (pipelineBody) pipelineBody.classList.remove('hidden');
      if (pipelineError) pipelineError.classList.add('hidden');
    };

    const showError = (err) => {
      if (pipelineLoading) pipelineLoading.classList.add('hidden');
      if (pipelineBody) pipelineBody.classList.add('hidden');
      if (pipelineError) pipelineError.classList.remove('hidden');
      if (pipelineErrorDetail) pipelineErrorDetail.textContent = err.message || 'Master pipeline service unavailable.';
    };

    const fetchMasterPipeline = async (fallback = false) => {
      showLoading();
      try {
        const pipelineData = await window.NexusAPI.getLatestMasterExecution();
        renderMasterPipeline(pipelineData);
        showContent();

        // Check connection status
        const status = await window.NexusAPI.getMasterStatus().catch(() => null);
        if (connectionBadge) {
          if (status && status.webhook_configured) {
            connectionBadge.innerHTML = '<span class="w-2 h-2 rounded-full bg-emerald-500"></span> Master Webhook Connected';
          } else {
            connectionBadge.innerHTML = '<span class="w-2 h-2 rounded-full bg-amber-500"></span> Reference Orchestrator Mode';
          }
        }
      } catch (err) {
        showError(err);
      }
    };

    // Bind triggers
    const triggerEvtBtn = document.getElementById('trigger-evt-004-btn');
    if (triggerEvtBtn) {
      triggerEvtBtn.addEventListener('click', async () => {
        showLoading();
        try {
          const res = await window.NexusAPI.triggerMasterTestEvent('EVT-TEST-004');
          renderMasterPipeline(res);
          showContent();
          window.NexusAPI.showToast('Master pipeline executed for EVT-TEST-004', 'success');
        } catch (err) {
          showError(err);
        }
      });
    }

    const refreshBtn = document.getElementById('refresh-pipeline-btn');
    if (refreshBtn) {
      refreshBtn.addEventListener('click', () => fetchMasterPipeline());
    }

    const retryBtn = document.getElementById('pipeline-retry-btn');
    if (retryBtn) {
      retryBtn.addEventListener('click', () => fetchMasterPipeline());
    }

    // Initial Load
    fetchMasterPipeline();
  };

  const initProcurement = async () => {
    if (!window.NexusAPI) return;

    try {
      const [pos, suppliers, alerts, recommendations] = await Promise.all([
        window.NexusAPI.getPurchaseOrders().catch(() => []),
        window.NexusAPI.getSuppliers().catch(() => []),
        window.NexusAPI.getAlerts().catch(() => []),
        window.NexusAPI.getRecommendations().catch(() => []),
      ]);

      // Populate Table
      const tbody = document.querySelector('main table tbody');
      if (tbody && pos && pos.length > 0) {
        const supplierMap = {};
        (suppliers || []).forEach((s) => {
          supplierMap[s.id] = s.name;
        });

        tbody.innerHTML = pos
          .map((po) => {
            const supplierName = supplierMap[po.supplier_id] || (po.supplier_id ? `Supplier #${po.supplier_id.slice(0, 4)}` : 'Supplier');
            const itemsSummary = po.items && po.items.length > 0
              ? `${po.items[0].product_name || 'Material'} (${po.items[0].quantity || '—'} units)`
              : 'Consignment Batch';
            const isDelayed = (po.status || '').toLowerCase().includes('delay');
            const statusClass = isDelayed
              ? 'bg-red-100 text-error'
              : po.status === 'in_transit'
              ? 'bg-slate-100 text-slate-700'
              : 'bg-emerald-100 text-emerald-800';

            return `
              <tr class="hover:bg-slate-50/75 transition-colors ${isDelayed ? 'bg-red-50/20' : ''}">
                <td class="py-3.5 px-5 font-mono font-medium text-indigo-600">${po.po_number || po.id?.slice(0, 8)}</td>
                <td class="py-3.5 px-5 font-medium text-slate-900">${supplierName}</td>
                <td class="py-3.5 px-5">${itemsSummary}</td>
                <td class="py-3.5 px-5 font-mono">$${Number(po.total_amount || 0).toLocaleString()}</td>
                <td class="py-3.5 px-5 font-mono ${isDelayed ? 'text-error font-medium' : 'text-slate-600'}">${po.expected_delivery_date || '—'}</td>
                <td class="py-3.5 px-5"><span class="inline-flex items-center px-2 py-0.5 rounded-full text-[11px] font-medium ${statusClass}">${po.status || 'Active'}</span></td>
                <td class="py-3.5 px-5 text-right"><button class="px-3 py-1 rounded bg-slate-900 text-white text-[11px] font-medium hover:bg-slate-800 transition-colors" type="button">Resolve</button></td>
              </tr>
            `;
          })
          .join('');
      }

      // Wire AI recommendation approve button
      const recCard = document.getElementById('aiRecommendationCard');
      const approveBtn = recCard?.querySelector('button.bg-indigo-600');
      const rec = (recommendations && recommendations.length > 0) ? recommendations[0] : null;

      if (approveBtn && rec) {
        approveBtn.addEventListener('click', async () => {
          approveBtn.disabled = true;
          approveBtn.textContent = 'Approving...';
          try {
            await window.NexusAPI.approveRecommendation(rec.id);
            approveBtn.className = 'px-4 py-2 rounded-lg bg-emerald-600 text-white text-xs font-medium';
            approveBtn.textContent = 'Approved';
            window.NexusAPI.showToast('Procurement expedite approved!', 'success');
          } catch (err) {
            approveBtn.disabled = false;
            approveBtn.textContent = 'Approve Expedite';
            window.NexusAPI.showToast(err.message || 'Approval failed', 'error');
          }
        });
      }
    } catch (e) {
      console.error('Error initializing Procurement data:', e);
    }
  };

  const initInventory = async () => {
    if (!window.NexusAPI) return;

    try {
      const [inventory, products, alerts, recommendations] = await Promise.all([
        window.NexusAPI.getInventory().catch(() => []),
        window.NexusAPI.getProducts().catch(() => []),
        window.NexusAPI.getAlerts().catch(() => []),
        window.NexusAPI.getRecommendations().catch(() => []),
      ]);

      const productMap = {};
      (products || []).forEach((p) => {
        productMap[p.id] = p;
      });

      // Populate Table
      const tbody = document.querySelector('main table tbody');
      if (tbody && inventory && inventory.length > 0) {
        tbody.innerHTML = inventory
          .map((inv) => {
            const product = productMap[inv.product_id] || { name: 'Item', sku: 'SKU-000' };
            const available = Number(inv.quantity_available || inv.quantity_on_hand || 0);
            const total = Number(inv.quantity_on_hand || (available + Number(inv.quantity_reserved || 0)));
            const reserved = Number(inv.quantity_reserved || 0);
            const floor = Number(inv.reorder_level || inv.reorder_threshold || 100);
            const isCritical = available < floor || (inv.status || '').toLowerCase().includes('critical') || (inv.status || '').toLowerCase().includes('low');
            const unit = inv.unit || product.unit || 'units';

            return `
              <tr class="hover:bg-slate-50/75 transition-colors ${isCritical ? 'bg-red-50/20' : ''}">
                <td class="py-3.5 px-5">
                  <div class="flex flex-col">
                    <span class="font-medium text-slate-900">${product.name}</span>
                    <span class="font-mono text-[11px] text-slate-400">${product.sku} · ${inv.warehouse_location || inv.location || 'Hub'}</span>
                  </div>
                </td>
                <td class="py-3.5 px-5 font-mono text-right text-slate-700">${total.toLocaleString()} ${unit}</td>
                <td class="py-3.5 px-5 font-mono text-right text-slate-500">${reserved.toLocaleString()} ${unit}</td>
                <td class="py-3.5 px-5 font-mono font-semibold text-right text-slate-900">${available.toLocaleString()} ${unit}</td>
                <td class="py-3.5 px-5 font-mono text-right text-slate-500">${floor.toLocaleString()} ${unit}</td>
                <td class="py-3.5 px-5 font-mono text-right ${isCritical ? 'text-error font-medium' : 'text-slate-600'}">${isCritical ? '1.8 Days' : '14.0 Days'}</td>
                <td class="py-3.5 px-5 text-center">
                  <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-[11px] font-medium ${isCritical ? 'bg-red-100 text-error' : 'bg-emerald-100 text-emerald-800'}">${isCritical ? 'Critical' : 'Optimal'}</span>
                </td>
                <td class="py-3.5 px-5 text-right"><button class="px-3 py-1 rounded bg-slate-900 text-white text-[11px] font-medium hover:bg-slate-800 transition-colors" type="button">Resolve</button></td>
              </tr>
            `;
          })
          .join('');
      }

      // Wire AI recommendation approve button
      const recCard = document.getElementById('aiRecommendationCard');
      const approveBtn = recCard?.querySelector('button.bg-indigo-600');
      const rec = (recommendations && recommendations.length > 0) ? recommendations[0] : null;

      if (approveBtn && rec) {
        approveBtn.addEventListener('click', async () => {
          approveBtn.disabled = true;
          approveBtn.textContent = 'Approving...';
          try {
            await window.NexusAPI.approveRecommendation(rec.id);
            approveBtn.className = 'px-4 py-2 rounded-lg bg-emerald-600 text-white font-medium text-sm';
            approveBtn.textContent = 'Approved';
            window.NexusAPI.showToast('Inventory rebalance approved!', 'success');
          } catch (err) {
            approveBtn.disabled = false;
            approveBtn.textContent = 'Approve Rebalance';
            window.NexusAPI.showToast(err.message || 'Approval failed', 'error');
          }
        });
      }
    } catch (e) {
      console.error('Error initializing Inventory data:', e);
    }
  };

  const initProduction = async () => {
    if (!window.NexusAPI) return;

    try {
      const [prodOrders, products, alerts, recommendations] = await Promise.all([
        window.NexusAPI.getProductionOrders().catch(() => []),
        window.NexusAPI.getProducts().catch(() => []),
        window.NexusAPI.getAlerts().catch(() => []),
        window.NexusAPI.getRecommendations().catch(() => []),
      ]);

      const productMap = {};
      (products || []).forEach((p) => {
        productMap[p.id] = p;
      });

      // Populate Table
      const tbody = document.querySelector('main table tbody');
      if (tbody && prodOrders && prodOrders.length > 0) {
        tbody.innerHTML = prodOrders
          .map((ord) => {
            const product = productMap[ord.product_id] || { name: 'Batch Product', sku: 'SKU-PRD' };
            const planned = Number(ord.target_quantity || ord.quantity_planned || 1000);
            const produced = Number(ord.completed_quantity || ord.quantity_produced || 0);
            const progress = planned > 0 ? Math.min(100, Math.round((produced / planned) * 100)) : 0;
            const isBlocked = (ord.status || '').toLowerCase().includes('block') || (ord.status || '').toLowerCase().includes('risk') || progress < 20;

            return `
              <tr class="hover:bg-slate-50/75 transition-colors ${isBlocked ? 'bg-red-50/20' : ''}">
                <td class="py-3.5 px-5 font-mono font-medium text-indigo-600">${ord.order_number || ord.id?.slice(0, 8)}</td>
                <td class="py-3.5 px-5">
                  <div class="flex flex-col">
                    <span class="font-medium text-slate-900">${product.name}</span>
                    <span class="text-[11px] text-slate-400 font-mono">${product.sku}</span>
                  </div>
                </td>
                <td class="py-3.5 px-5">
                  <div class="flex items-center gap-1.5">
                    <span class="w-2 h-2 rounded-full ${isBlocked ? 'bg-error' : 'bg-emerald-500'}"></span>
                    <span>Line ${ord.line_id || ord.production_line || '02'}</span>
                  </div>
                </td>
                <td class="py-3.5 px-5 font-mono">${planned.toLocaleString()} Units</td>
                <td class="py-3.5 px-5">
                  <div class="w-32 flex flex-col gap-1">
                    <div class="flex justify-between items-center font-mono text-[11px] text-slate-500">
                      <span>${progress}%</span>
                      <span>${produced.toLocaleString()} / ${planned.toLocaleString()}</span>
                    </div>
                    <div class="w-full bg-slate-100 h-1.5 rounded-full overflow-hidden">
                      <div class="${isBlocked ? 'bg-error' : 'bg-indigo-600'} h-full rounded-full" style="width: ${progress}%;"></div>
                    </div>
                  </div>
                </td>
                <td class="py-3.5 px-5">
                  <span class="inline-flex items-center px-2 py-0.5 rounded-full text-[11px] font-medium ${isBlocked ? 'bg-red-100 text-error' : 'bg-slate-100 text-slate-700'}">${isBlocked ? 'Critical' : 'On Track'}</span>
                </td>
                <td class="py-3.5 px-5 text-right"><button class="px-3 py-1 rounded bg-slate-900 text-white text-[11px] font-medium hover:bg-slate-800 transition-colors" type="button">Resolve</button></td>
              </tr>
            `;
          })
          .join('');
      }

      // Wire AI recommendation approve button
      const recCard = document.getElementById('aiRecommendationCard');
      const approveBtn = recCard?.querySelector('button.bg-indigo-600');
      const rec = (recommendations && recommendations.length > 0) ? recommendations[0] : null;

      if (approveBtn && rec) {
        approveBtn.addEventListener('click', async () => {
          approveBtn.disabled = true;
          approveBtn.textContent = 'Approving...';
          try {
            await window.NexusAPI.approveRecommendation(rec.id);
            approveBtn.className = 'px-4 py-2 rounded-lg bg-emerald-600 text-white text-xs font-medium';
            approveBtn.textContent = 'Approved';
            window.NexusAPI.showToast('Production schedule swap approved!', 'success');
          } catch (err) {
            approveBtn.disabled = false;
            approveBtn.textContent = 'Approve Schedule Swap';
            window.NexusAPI.showToast(err.message || 'Approval failed', 'error');
          }
        });
      }
    } catch (e) {
      console.error('Error initializing Production data:', e);
    }
  };

  const initLogistics = async () => {
    if (!window.NexusAPI) return;

    try {
      const [shipments, alerts, recommendations] = await Promise.all([
        window.NexusAPI.getShipments().catch(() => []),
        window.NexusAPI.getAlerts().catch(() => []),
        window.NexusAPI.getRecommendations().catch(() => []),
      ]);

      // Populate Table
      const tbody = document.querySelector('main table tbody');
      if (tbody && shipments && shipments.length > 0) {
        tbody.innerHTML = shipments
          .map((sh) => {
            const isDelayed = (sh.status || '').toLowerCase().includes('delay') || (sh.status || '').toLowerCase().includes('risk');
            const statusBadgeClass = isDelayed
              ? 'bg-red-100 text-error'
              : sh.status === 'out_for_delivery'
              ? 'bg-emerald-100 text-emerald-800'
              : 'bg-slate-100 text-slate-700';

            return `
              <tr class="hover:bg-slate-50/75 transition-colors ${isDelayed ? 'bg-red-50/20' : ''}">
                <td class="py-3.5 px-5 font-mono font-medium text-indigo-600">${sh.tracking_number || sh.id?.slice(0, 8)}</td>
                <td class="py-3.5 px-5">
                  <div class="font-medium text-slate-900">${sh.carrier || 'Direct Freight'}</div>
                  <div class="text-[11px] text-slate-500 font-mono">${sh.origin || 'Origin'} → ${sh.destination || 'Hub'}</div>
                </td>
                <td class="py-3.5 px-5 font-medium text-slate-900">${sh.destination || 'Distribution Center'}</td>
                <td class="py-3.5 px-5">
                  <div>Consignment Batch</div>
                  <div class="text-[11px] text-slate-400 font-mono">${sh.po_id ? `PO-${sh.po_id.slice(0, 4)}` : 'PO-8821'}</div>
                </td>
                <td class="py-3.5 px-5 font-mono ${isDelayed ? 'text-error font-medium' : 'text-slate-600'}">${sh.estimated_delivery || '—'}</td>
                <td class="py-3.5 px-5"><span class="inline-flex items-center px-2 py-0.5 rounded-full text-[11px] font-medium ${statusBadgeClass}">${sh.status || 'Active'}</span></td>
                <td class="py-3.5 px-5"><span class="inline-flex items-center px-2 py-0.5 rounded-full text-[11px] font-semibold ${isDelayed ? 'bg-red-600 text-white' : 'bg-slate-100 text-slate-600'}">${isDelayed ? 'Critical' : 'Normal'}</span></td>
                <td class="py-3.5 px-5 text-right"><button class="px-3 py-1 rounded bg-slate-900 text-white text-[11px] font-medium hover:bg-slate-800 transition-colors" type="button">Resolve</button></td>
              </tr>
            `;
          })
          .join('');
      }

      // Wire AI recommendation approve button
      const recCard = document.getElementById('aiRecommendationCard');
      const approveBtn = recCard?.querySelector('button.bg-indigo-600');
      const rec = (recommendations && recommendations.length > 0) ? recommendations[0] : null;

      if (approveBtn && rec) {
        approveBtn.addEventListener('click', async () => {
          approveBtn.disabled = true;
          approveBtn.textContent = 'Approving...';
          try {
            await window.NexusAPI.approveRecommendation(rec.id);
            approveBtn.className = 'px-4 py-2 rounded-lg bg-emerald-600 text-white text-xs font-medium';
            approveBtn.textContent = 'Approved';
            window.NexusAPI.showToast('Logistics direct route approved!', 'success');
          } catch (err) {
            approveBtn.disabled = false;
            approveBtn.textContent = 'Approve Direct Route';
            window.NexusAPI.showToast(err.message || 'Approval failed', 'error');
          }
        });
      }
    } catch (e) {
      console.error('Error initializing Logistics data:', e);
    }
  };

  // Enforce access control
  enforceAccessControl();

  if (page !== 'login' && page !== 'home') {
    const navMap = {
      controlTower: 'controlTower',
      procurement: 'procurement',
      inventory: 'inventory',
      production: 'production',
      logistics: 'logistics',
    };
    setActiveNav(navMap[page] || 'controlTower');
    bindUserHeader();
  }

  bindThemeToggle();
  bindLogin();
  bindLogout();
  bindDismissableCards();

  // Trigger page-specific data fetchers
  if (page === 'controlTower') {
    initControlTower();
  } else if (page === 'procurement') {
    initProcurement();
  } else if (page === 'inventory') {
    initInventory();
  } else if (page === 'production') {
    initProduction();
  } else if (page === 'logistics') {
    initLogistics();
  }
})();
