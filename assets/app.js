(() => {
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
    Procurement: { email: 'm.vance@nexustower.internal', tag: 'ROLE: PROC-MG', href: pages.procurement, pageKey: 'procurement' },
    Inventory: { email: 's.chen@nexustower.internal', tag: 'ROLE: INVT-LEAD', href: pages.inventory, pageKey: 'inventory' },
    Production: { email: 'k.novak@nexustower.internal', tag: 'ROLE: PROD-DIR', href: pages.production, pageKey: 'production' },
    Logistics: { email: 'd.morales@nexustower.internal', tag: 'ROLE: LOGS-SPEC', href: pages.logistics, pageKey: 'logistics' },
    'Control Tower': { email: 'ops-admin@nexustower.internal', tag: 'ROLE: TOWER-ROOT', href: pages.controlTower, pageKey: 'controlTower' },
  };

  // Map each dashboard page to its allowed role key
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
      if (roleTag) roleTag.textContent = role.tag;
      if (loginButton) loginButton.dataset.target = role.href;
      if (loginButton) loginButton.dataset.role = roleName;
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

    setPersona('Procurement');

    form.addEventListener('submit', (event) => {
      event.preventDefault();
      const roleName = loginButton?.dataset.role || 'Procurement';
      const target = loginButton?.dataset.target || pages.controlTower;

      // Store the selected role in sessionStorage for access control
      sessionStorage.setItem('nexus-role', roleName);
      sessionStorage.setItem('nexus-role-page', roleTargets[roleName]?.pageKey || 'controlTower');

      window.location.href = target;
    });
  };

  const bindLogout = () => {
    const logoutBtn = document.getElementById('logout-btn');
    if (!logoutBtn) return;

    logoutBtn.addEventListener('click', () => {
      sessionStorage.removeItem('nexus-role');
      sessionStorage.removeItem('nexus-role-page');
      window.location.href = pages.login;
    });
  };

  const enforceAccessControl = () => {
    if (page === 'login') return;

    const storedRole = sessionStorage.getItem('nexus-role');
    const storedRolePage = sessionStorage.getItem('nexus-role-page');

    // If no role stored, redirect to login
    if (!storedRole || !storedRolePage) {
      window.location.href = pages.login;
      return;
    }

    // Control Tower role has cross-domain access to all dashboards
    const isControlTower = storedRolePage === 'controlTower';

    // For non-Control-Tower roles, enforce page restriction
    if (!isControlTower && pageRoleMap[page] !== storedRolePage) {
      const role = roleTargets[storedRole];
      if (role) {
        window.location.href = role.href;
      } else {
        window.location.href = pages.login;
      }
      return;
    }

    // Remove the sidebar navigation for non-Control-Tower roles since only the assigned dashboard should be visible
    if (!isControlTower) {
      const sidebar = document.querySelector('aside');
      if (sidebar) {
        sidebar.remove();
      }

      // Adjust main content padding since sidebar is removed
      const contentWrapper = document.querySelector('.lg\\:pl-64');
      if (contentWrapper) {
        contentWrapper.classList.remove('lg:pl-64');
      }
    }
  };

  const bindControlTowerAction = () => {
    const button = document.getElementById('approve-action');
    const panel = document.getElementById('action-panel');
    if (!button || !panel) return;

    button.addEventListener('click', () => {
      panel.innerHTML = `
        <div class="flex items-center justify-between py-1 gap-6">
          <div class="flex items-center gap-3">
            <span class="w-10 h-10 rounded-full bg-emerald-50 text-emerald-600 flex items-center justify-center shrink-0">
              <span class="material-symbols-outlined text-[22px]">check_circle</span>
            </span>
            <div>
              <div class="text-sm font-medium text-slate-900">Action approved and transmitted to ERP</div>
              <div class="text-xs text-slate-500">Tanker priority dispatched • Reference #NX-49102</div>
            </div>
          </div>
          <span class="text-xs font-mono text-slate-400 shrink-0">Status: Executing</span>
        </div>
      `;
    });
  };

  const bindDismissableCards = () => {
    document.querySelectorAll('[data-dismiss-target]').forEach((button) => {
      button.addEventListener('click', () => {
        const target = document.getElementById(button.dataset.dismissTarget);
        if (target) target.remove();
      });
    });
  };

  // Enforce access control first (before any other page logic)
  enforceAccessControl();

  if (page !== 'login') {
    const navMap = {
      controlTower: 'controlTower',
      procurement: 'procurement',
      inventory: 'inventory',
      production: 'production',
      logistics: 'logistics',
    };
    setActiveNav(navMap[page] || 'controlTower');
  }

  bindThemeToggle();
  bindLogin();
  bindLogout();
  bindControlTowerAction();
  bindDismissableCards();
})();