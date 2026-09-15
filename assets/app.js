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

  const initControlTower = async () => {
    if (!window.NexusAPI) return;

    try {
      const [alerts, risks, recommendations, events, inventory, pos, prodOrders, shipments] = await Promise.all([
        window.NexusAPI.getAlerts().catch(() => []),
        window.NexusAPI.getRisks().catch(() => []),
        window.NexusAPI.getRecommendations().catch(() => []),
        window.NexusAPI.getEvents(10).catch(() => []),
        window.NexusAPI.getInventory().catch(() => []),
        window.NexusAPI.getPurchaseOrders().catch(() => []),
        window.NexusAPI.getProductionOrders().catch(() => []),
        window.NexusAPI.getShipments().catch(() => []),
      ]);

      // Wire AI Recommendation action button
      const approveBtn = document.getElementById('approve-action');
      const actionPanel = document.getElementById('action-panel');
      const activeRec = (recommendations && recommendations.length > 0) ? recommendations[0] : null;

      if (actionPanel && activeRec) {
        const titleEl = actionPanel.querySelector('h3');
        const descEl = actionPanel.querySelector('p');
        const confEl = actionPanel.querySelector('.text-slate-400');

        if (titleEl && activeRec.title) titleEl.textContent = activeRec.title;
        if (descEl && activeRec.description) {
          descEl.innerHTML = `${activeRec.description} • Expected Impact: <strong class="text-slate-900">${activeRec.expected_impact || '$14,200 protected'}</strong>`;
        }
        if (confEl && activeRec.confidence_score) {
          confEl.textContent = `${Math.round(activeRec.confidence_score * 100)}% system confidence`;
        }
      }

      if (approveBtn && actionPanel) {
        approveBtn.addEventListener('click', async () => {
          approveBtn.disabled = true;
          approveBtn.textContent = 'Transmitting...';
          try {
            if (activeRec && activeRec.id) {
              await window.NexusAPI.approveRecommendation(activeRec.id);
            }
            actionPanel.innerHTML = `
              <div class="flex items-center justify-between py-1 gap-6">
                <div class="flex items-center gap-3">
                  <span class="w-10 h-10 rounded-full bg-emerald-50 text-emerald-600 flex items-center justify-center shrink-0">
                    <span class="material-symbols-outlined text-[22px]">check_circle</span>
                  </span>
                  <div>
                    <div class="text-sm font-medium text-slate-900">Action approved and transmitted to ERP</div>
                    <div class="text-xs text-slate-500">Execution in progress • Corridors prioritized</div>
                  </div>
                </div>
                <span class="text-xs font-mono text-emerald-600 font-medium shrink-0">Status: Executing</span>
              </div>
            `;
            window.NexusAPI.showToast('Recommendation successfully approved and dispatched!', 'success');
          } catch (err) {
            approveBtn.disabled = false;
            approveBtn.textContent = 'Approve Action';
            window.NexusAPI.showToast(err.message || 'Approval failed', 'error');
          }
        });
      }
    } catch (e) {
      console.error('Error initializing Control Tower data:', e);
    }
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
