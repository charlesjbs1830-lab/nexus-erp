/**
 * Nexus Jr. | ERP Gestão & Finanças 2.0
 * Lógica Front-End e Integração com FastAPI Standalone
 * Controle de Acesso RBAC, CPQ Paramétrico, Gantt com Travas de Mentor,
 * Repositório de Ativos com Versionamento, Timesheet com Scope Creep,
 * DRE Gerencial, Visual Analytics (Chart.js), Feed de Atividades, Painel VPGG e Exportações.
 */

// Estado Global da Aplicação
const state = {
  user: JSON.parse(localStorage.getItem("nexus_user")) || {
    id: 1,
    nome: "Charles",
    email: "charles@nexusjr.com",
    role: "presidente",
    cargo: "Diretor Presidente",
    area: "Presidência"
  },
  activeView: "dashboard",
  financeSubTab: "dre",
  forecastHorizon: 24,
  forecastMetric: "saldo_acumulado",
  forecasting: null,
  services: [],
  proposals: [],
  projects: [],
  assets: [],
  timesheet: [],
  scopeAlerts: [],
  dre: null,
  kpis: null,
  activities: [],
  members: [],
  charts: {},
  selectedMilestoneForMentor: null,
  currentEditingMemberId: null
};

// ==============================================================================
// INICIALIZAÇÃO DA APLICAÇÃO
// ==============================================================================
document.addEventListener("DOMContentLoaded", async () => {
  updateUserInterface();
  setupTodayDate();
  await loadInitialData();
  switchView("dashboard");
});

function setupTodayDate() {
  const tsDate = document.getElementById("ts-date");
  if (tsDate) {
    const today = new Date().toISOString().split("T")[0];
    tsDate.value = today;
  }
}

function updateUserInterface() {
  const nameEl = document.getElementById("user-display-name");
  const roleEl = document.getElementById("user-display-role");
  const initialsEl = document.getElementById("user-avatar-initials");
  const tsName = document.getElementById("ts-consultant-name");
  const tsEmail = document.getElementById("ts-consultant-email");

  if (nameEl) nameEl.textContent = state.user.nome;
  if (roleEl) roleEl.textContent = state.user.cargo || state.user.role;
  if (initialsEl) {
    const initials = state.user.nome.split(" ").map(n => n[0]).slice(0, 2).join("").toUpperCase();
    initialsEl.textContent = initials || "NX";
  }
  if (tsName) tsName.value = state.user.nome;
  if (tsEmail) tsEmail.value = state.user.email;
}

async function loadInitialData() {
  try {
    const [servicesRes, proposalsRes, projectsRes, assetsRes, timesheetRes, dreRes, kpiRes, actRes, memRes, forecastRes] = await Promise.all([
      fetch("/api/business/services").then(r => r.json()),
      fetch("/api/business/cpq/proposals").then(r => r.json()),
      fetch("/api/business/projects/gantt").then(r => r.json()),
      fetch("/api/business/knowledge/assets").then(r => r.json()),
      fetch("/api/business/timesheet").then(r => r.json()),
      fetch("/api/business/finance/dre-by-project").then(r => r.json()),
      fetch("/api/business/kpis/overview").then(r => r.json()),
      fetch("/api/business/activities").then(r => r.json()),
      fetch("/api/business/members").then(r => r.json()),
      fetch("/api/business/finance/forecasting?horizon_months=24").then(r => r.json())
    ]);

    state.services = servicesRes.services || [];
    state.proposals = proposalsRes.proposals || [];
    state.projects = projectsRes.projects || [];
    state.assets = assetsRes.assets || [];
    state.timesheet = timesheetRes.entries || [];
    state.scopeAlerts = timesheetRes.active_scope_alerts || [];
    state.dre = dreRes;
    state.kpis = kpiRes;
    state.activities = actRes.activities || [];
    state.members = memRes.members || [];
    state.forecasting = forecastRes;

    populateCPQServicesDropdown();
    populateTimesheetProjects();
    populateDREFilterDropdown();
    updateKPIDashboard(kpiRes);
    renderActivityFeed();
    renderMembersTable();
    if (forecastRes) {
      renderForecastingDashboard(forecastRes);
      renderForecastingTable();
    }
  } catch (error) {
    console.error("[Nexus Jr.] Erro ao carregar dados iniciais:", error);
  }
}

// ==============================================================================
// NAVEGAÇÃO ENTRE VISTAS (TAB SWITCHER)
// ==============================================================================
const viewsMetadata = {
  dashboard: { title: "Painel Executivo (BI & Metas PE)", icon: "fa-chart-pie" },
  cpq_pipeline: { title: "Pipeline Comercial & CPQ Paramétrico", icon: "fa-calculator" },
  projetos_gantt: { title: "Gestão de Projetos, Marcos & Travas de Mentores", icon: "fa-bars-progress" },
  ativos_valuation: { title: "Repositório de Ativos Intelectuais & Modelos", icon: "fa-book-bookmark" },
  timesheet_capacidade: { title: "Timesheet & Alocação de Capacidade", icon: "fa-clock" },
  financeiro_compliance: { title: "Tesouraria, Compliance & DRE por Centro de Custo", icon: "fa-scale-balanced" },
  membros_vpgg: { title: "Gente & Gestão (VPGG) & Controle de RBAC", icon: "fa-users-gear" }
};

function switchView(viewName) {
  state.activeView = viewName;

  // Atualizar botões da sidebar
  Object.keys(viewsMetadata).forEach(name => {
    const navBtn = document.getElementById(`nav-${name}`);
    const viewSection = document.getElementById(`view-${name}`);

    if (navBtn) {
      if (name === viewName) {
        navBtn.classList.remove("tab-inactive");
        navBtn.classList.add("tab-active");
        const icon = navBtn.querySelector("i");
        if (icon) icon.className = `fa-solid ${viewsMetadata[name].icon} w-5 text-center text-emerald-400`;
      } else {
        navBtn.classList.remove("tab-active");
        navBtn.classList.add("tab-inactive");
        const icon = navBtn.querySelector("i");
        if (icon) icon.className = `fa-solid ${viewsMetadata[name].icon} w-5 text-center text-slate-400`;
      }
    }

    if (viewSection) {
      if (name === viewName) {
        viewSection.classList.remove("hidden");
      } else {
        viewSection.classList.add("hidden");
      }
    }
  });

  // Atualizar Header
  const titleEl = document.getElementById("page-title");
  const iconEl = document.getElementById("page-icon");
  if (titleEl && viewsMetadata[viewName]) {
    titleEl.textContent = viewsMetadata[viewName].title;
  }
  if (iconEl && viewsMetadata[viewName]) {
    iconEl.innerHTML = `<i class="fa-solid ${viewsMetadata[viewName].icon}"></i>`;
  }

  // Renderizações específicas de tela
  if (viewName === "dashboard") {
    renderDashboard();
    setTimeout(renderDashboardCharts, 50);
  }
  if (viewName === "cpq_pipeline") renderCPQView();
  if (viewName === "projetos_gantt") renderProjectsGantt();
  if (viewName === "ativos_valuation") renderAssets();
  if (viewName === "timesheet_capacidade") renderTimesheetView();
  if (viewName === "financeiro_compliance") {
    if (state.financeSubTab === "dre") {
      renderDRETable();
      setTimeout(renderDREChart, 50);
    } else {
      if (!state.forecasting) {
        loadForecastingData();
      } else {
        renderForecastingDashboard(state.forecasting);
        setTimeout(() => renderForecastingCharts(state.forecasting), 50);
        renderForecastingTable();
      }
    }
  }
  if (viewName === "membros_vpgg") renderMembersTable();
}

// ==============================================================================
// 1. MÓDULO DASHBOARD & VISUAL ANALYTICS (CHART.JS)
// ==============================================================================
function updateKPIDashboard(kpi) {
  if (!kpi) return;
  const fatEl = document.getElementById("kpi-faturamento");
  const supEl = document.getElementById("kpi-superavit");
  const hhEl = document.getElementById("kpi-hh");
  const alertEl = document.getElementById("kpi-alerts");
  const margemBanner = document.getElementById("kpi-banner-margem");
  const topbarSup = document.getElementById("topbar-superavit");

  if (fatEl) fatEl.textContent = formatCurrency(kpi.faturamento_acumulado);
  if (supEl) supEl.textContent = formatCurrency(kpi.superavit_estatutario);
  if (hhEl) hhEl.textContent = `${kpi.total_hh_executado} h / ${kpi.total_hh_orcado} h`;
  if (alertEl) alertEl.textContent = `${kpi.alertas_scope_creep_ativos} Alerta(s) Ativo(s)`;
  if (margemBanner) margemBanner.textContent = `${kpi.margem_contribuicao_pct}%`;
  if (topbarSup) topbarSup.textContent = formatCurrency(kpi.superavit_estatutario);
}

function renderDashboard() {
  const tbody = document.getElementById("dash-projects-tbody");
  if (!tbody) return;

  tbody.innerHTML = state.projects.map(p => {
    const hasScopeAlert = p.scope_creep_alert;
    const pendingMentor = p.milestones && p.milestones.some(m => m.requires_mentor_approval && m.mentor_approval_status !== "aprovado");

    let statusBadge = `<span class="badge-active">Em Andamento</span>`;
    if (pendingMentor) {
      statusBadge = `<span class="badge-mentor"><i class="fa-solid fa-lock text-[10px] mr-1"></i>Trava de Mentor</span>`;
    }
    if (hasScopeAlert) {
      statusBadge += ` <span class="badge-alert ml-1"><i class="fa-solid fa-triangle-exclamation mr-1"></i>Escopo ≥75%</span>`;
    }

    return `
      <tr class="hover:bg-slate-50 transition-colors">
        <td class="py-3 px-4 font-semibold text-slate-800">
          ${p.name}
          <div class="text-xs text-slate-500 font-normal">Cliente: ${p.client_name} &bull; Gerente: ${p.manager_name}</div>
        </td>
        <td class="py-3 px-4 text-xs font-medium text-slate-600">${p.macro_area}</td>
        <td class="py-3 px-4 text-xs font-mono text-slate-700">${p.lead_time_weeks} semanas</td>
        <td class="py-3 px-4 text-xs font-mono">
          <span class="font-bold ${p.consumed_hh > p.total_budgeted_hh ? 'text-rose-600' : 'text-slate-800'}">${p.consumed_hh} h</span> / ${p.total_budgeted_hh} h
        </td>
        <td class="py-3 px-4">
          <div class="w-full bg-slate-200 rounded-full h-2.5 overflow-hidden">
            <div class="bg-emerald-600 h-2.5 rounded-full" style="width: ${p.progress_pct}%"></div>
          </div>
          <span class="text-[11px] text-slate-500 font-mono mt-0.5 inline-block">${p.progress_pct}% concluído</span>
        </td>
        <td class="py-3 px-4">${statusBadge}</td>
      </tr>
    `;
  }).join("");
}

function renderDashboardCharts() {
  if (!state.kpis || !state.kpis.charts) return;

  // 1. Gráfico de Evolução do Faturamento Acumulado (Linha / Área)
  const ctxRev = document.getElementById("chart-revenue-evolution");
  if (ctxRev) {
    if (state.charts.revenue) state.charts.revenue.destroy();

    const dataRev = state.kpis.charts.revenue_evolution;
    state.charts.revenue = new Chart(ctxRev, {
      type: "line",
      data: {
        labels: dataRev.labels,
        datasets: [
          {
            label: "Meta PE 2026 (R$)",
            data: dataRev.meta_planejada,
            borderColor: "#0b1d3a",
            borderDash: [5, 5],
            borderWidth: 2,
            pointRadius: 3,
            fill: false,
            tension: 0.3
          },
          {
            label: "Realizado Acumulado (R$)",
            data: dataRev.realizado_acumulado,
            borderColor: "#059669",
            backgroundColor: "rgba(5, 150, 105, 0.12)",
            borderWidth: 3,
            pointRadius: 4,
            pointBackgroundColor: "#059669",
            fill: true,
            tension: 0.3
          }
        ]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { position: "top", labels: { boxWidth: 12, font: { size: 11, family: "system-ui" } } },
          tooltip: {
            callbacks: {
              label: (ctx) => ` ${ctx.dataset.label}: ${formatCurrency(ctx.raw)}`
            }
          }
        },
        scales: {
          y: {
            beginAtZero: true,
            ticks: {
              callback: (val) => "R$ " + (val / 1000) + "k",
              font: { size: 10 }
            },
            grid: { color: "#f1f5f9" }
          },
          x: {
            grid: { display: false },
            ticks: { font: { size: 11 } }
          }
        }
      }
    });
  }

  // 2. Gráfico de Homem-Hora Orçado vs. Executado por Projeto (Barras Agrupadas)
  const ctxHH = document.getElementById("chart-hh-comparison");
  if (ctxHH) {
    if (state.charts.hh) state.charts.hh.destroy();

    const dataHH = state.kpis.charts.hh_comparison;
    state.charts.hh = new Chart(ctxHH, {
      type: "bar",
      data: {
        labels: dataHH.labels,
        datasets: [
          {
            label: "HH Orçado",
            data: dataHH.orcado,
            backgroundColor: "#0b1d3a",
            borderRadius: 4
          },
          {
            label: "HH Executado",
            data: dataHH.executado,
            backgroundColor: "#059669",
            borderRadius: 4
          }
        ]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { position: "top", labels: { boxWidth: 12, font: { size: 11 } } },
          tooltip: {
            callbacks: {
              label: (ctx) => ` ${ctx.dataset.label}: ${ctx.raw} horas`
            }
          }
        },
        scales: {
          y: {
            beginAtZero: true,
            ticks: { font: { size: 10 } },
            grid: { color: "#f1f5f9" }
          },
          x: {
            grid: { display: false },
            ticks: { font: { size: 10 } }
          }
        }
      }
    });
  }
}

// 3. Gráfico de Distribuição do OBZ / Destinação (Donut)
function renderDREChart() {
  if (!state.kpis || !state.kpis.charts) return;

  const ctxOBZ = document.getElementById("chart-obz-distribution");
  if (ctxOBZ) {
    if (state.charts.obz) state.charts.obz.destroy();

    const dataOBZ = state.kpis.charts.obz_distribution;
    state.charts.obz = new Chart(ctxOBZ, {
      type: "doughnut",
      data: {
        labels: dataOBZ.labels,
        datasets: [
          {
            data: dataOBZ.values,
            backgroundColor: dataOBZ.colors,
            borderWidth: 2,
            borderColor: "#ffffff"
          }
        ]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        cutout: "68%",
        plugins: {
          legend: { display: false },
          tooltip: {
            callbacks: {
              label: (ctx) => ` ${ctx.label}: ${formatCurrency(ctx.raw)}`
            }
          }
        }
      }
    });
  }
}

// ==============================================================================
// 2. MÓDULO FEED DE ATIVIDADES EM TEMPO REAL
// ==============================================================================
function renderActivityFeed(filterType = "ALL") {
  const container = document.getElementById("activity-feed-container");
  if (!container) return;

  const filtered = filterType === "ALL" 
    ? state.activities 
    : state.activities.filter(a => a.action_type === filterType);

  if (filtered.length === 0) {
    container.innerHTML = `<div class="text-center py-6 text-slate-500 text-xs">Nenhuma atividade registrada para esta categoria.</div>`;
    return;
  }

  const icons = {
    mentor_approval: { icon: "fa-graduation-cap", color: "text-emerald-700 bg-emerald-50 border-emerald-200" },
    scope_alert: { icon: "fa-triangle-exclamation", color: "text-amber-700 bg-amber-50 border-amber-200" },
    timesheet: { icon: "fa-clock", color: "text-blue-700 bg-blue-50 border-blue-200" },
    cpq_proposal: { icon: "fa-file-invoice-dollar", color: "text-indigo-700 bg-indigo-50 border-indigo-200" },
    finance: { icon: "text-emerald-800 bg-emerald-100 border-emerald-300", icon: "fa-coins" },
    member_management: { icon: "fa-user-check", color: "text-purple-700 bg-purple-50 border-purple-200" }
  };

  container.innerHTML = filtered.map(a => {
    const meta = icons[a.action_type] || { icon: "fa-circle-info", color: "text-slate-700 bg-slate-50 border-slate-200" };
    return `
      <div class="flex items-start gap-3 p-3 rounded-lg border border-slate-100 hover:bg-slate-50/80 transition-colors">
        <div class="w-8 h-8 rounded-lg flex items-center justify-center border ${meta.color} flex-shrink-0 text-sm">
          <i class="fa-solid ${meta.icon}"></i>
        </div>
        <div class="flex-1 min-w-0">
          <div class="flex items-center justify-between">
            <h5 class="text-xs font-bold text-slate-800 truncate">${a.title}</h5>
            <span class="text-[10px] text-slate-400 font-mono">${a.created_at || 'Agora'}</span>
          </div>
          <p class="text-xs text-slate-600 mt-0.5 line-clamp-2">${a.description}</p>
          <div class="flex items-center gap-2 mt-1 text-[11px] text-slate-400">
            <span><strong>${a.actor_name}</strong> (${a.actor_role})</span>
            ${a.project_name ? `<span>&bull; ${a.project_name}</span>` : ""}
          </div>
        </div>
      </div>
    `;
  }).join("");
}

function filterActivities(type) {
  renderActivityFeed(type);
}

// ==============================================================================
// 3. MÓDULO GESTÃO DE MEMBROS E EQUIPA (PAINEL VPGG / RBAC)
// ==============================================================================
function renderMembersTable(membersToRender = null) {
  const tbody = document.getElementById("vpgg-members-tbody");
  const countBadge = document.getElementById("member-count-badge");
  const kpiAtivos = document.getElementById("vpgg-kpi-ativos");
  const kpiAlocados = document.getElementById("vpgg-kpi-alocados");
  const kpiLideranca = document.getElementById("vpgg-kpi-lideranca");

  const list = membersToRender || state.members;

  if (kpiAtivos) kpiAtivos.textContent = state.members.filter(m => m.status === "ativo").length;
  if (kpiAlocados) kpiAlocados.textContent = state.members.filter(m => m.cost_center && !m.cost_center.includes("Presidência")).length;
  if (kpiLideranca) kpiLideranca.textContent = state.members.filter(m => ["presidente", "diretor", "gerente"].includes(m.role)).length;
  if (countBadge) countBadge.textContent = `${list.length} membro(s) listado(s)`;

  if (!tbody) return;

  if (list.length === 0) {
    tbody.innerHTML = `<tr><td colspan="7" class="py-8 text-center text-slate-500 text-xs">Nenhum membro encontrado com os filtros selecionados.</td></tr>`;
    return;
  }

  const roleBadges = {
    presidente: `<span class="badge-critical"><i class="fa-solid fa-crown text-[10px] mr-1"></i>Presidente</span>`,
    diretor: `<span class="badge-mentor"><i class="fa-solid fa-shield text-[10px] mr-1"></i>Diretoria</span>`,
    gerente: `<span class="badge-active"><i class="fa-solid fa-user-tie text-[10px] mr-1"></i>Gerência</span>`,
    assessor: `<span class="text-[11px] bg-slate-100 text-slate-700 font-semibold px-2 py-0.5 rounded border border-slate-200">Consultor/Assessor</span>`
  };

  tbody.innerHTML = list.map(m => {
    const isDesligado = m.status === "desligado";
    const statusBadge = isDesligado
      ? `<span class="badge-alert">Desligado / Turnover</span>`
      : `<span class="badge-approved"><i class="fa-solid fa-check mr-1"></i>Ativo Regular</span>`;

    const initials = m.nome.split(" ").map(n => n[0]).slice(0, 2).join("").toUpperCase();

    return `
      <tr class="hover:bg-slate-50 transition-colors ${isDesligado ? 'opacity-60 bg-slate-50/50' : ''}">
        <td class="py-3 px-4">
          <div class="flex items-center gap-2.5">
            <div class="w-8 h-8 rounded-full bg-emerald-100 text-emerald-800 font-bold text-xs flex items-center justify-center flex-shrink-0">
              ${initials}
            </div>
            <div class="min-w-0">
              <span class="font-bold text-slate-900 block truncate">${m.nome}</span>
              <span class="text-xs text-slate-400 font-mono block truncate">${m.email}</span>
            </div>
          </div>
        </td>
        <td class="py-3 px-4 text-xs font-semibold text-slate-800">${m.cargo}</td>
        <td class="py-3 px-4 text-xs font-medium text-slate-600">${m.area}</td>
        <td class="py-3 px-4 text-xs font-mono text-slate-700">${m.cost_center || 'Geral'}</td>
        <td class="py-3 px-4 whitespace-nowrap">${roleBadges[m.role] || m.role}</td>
        <td class="py-3 px-4 whitespace-nowrap">
          <div class="text-[11px] font-mono text-slate-500">${m.turnover_cycle}</div>
          <div class="mt-0.5">${statusBadge}</div>
        </td>
        <td class="py-3 px-4 text-right whitespace-nowrap">
          <div class="flex items-center justify-end gap-1.5">
            <button onclick="toggleMemberStatus(${m.id})" class="text-slate-500 hover:text-emerald-700 p-1.5 rounded hover:bg-slate-100 transition" title="${isDesligado ? 'Reativar Membro' : 'Inativar / Desligar'}">
              <i class="fa-solid ${isDesligado ? 'fa-user-check text-emerald-600' : 'fa-user-slash text-amber-600'} text-xs"></i>
            </button>
            <button onclick="openMemberModal(${m.id})" class="text-slate-600 hover:text-emerald-700 p-1.5 rounded hover:bg-slate-100 transition" title="Editar Atribuições">
              <i class="fa-solid fa-pen-to-square text-xs"></i>
            </button>
            ${!isDesligado ? `
              <button onclick="deleteMember(${m.id}, '${escapeHtml(m.nome)}')" class="text-slate-400 hover:text-rose-600 p-1.5 rounded hover:bg-rose-50 transition" title="Registrar Turnover / Desligar">
                <i class="fa-solid fa-user-xmark text-xs"></i>
              </button>
            ` : ""}
          </div>
        </td>
      </tr>
    `;
  }).join("");
}

function filterMembers() {
  const search = document.getElementById("member-search-input")?.value.toLowerCase() || "";
  const area = document.getElementById("member-area-filter")?.value || "ALL";
  const role = document.getElementById("member-role-filter")?.value || "ALL";

  const filtered = state.members.filter(m => {
    const matchSearch = m.nome.toLowerCase().includes(search) || m.email.toLowerCase().includes(search) || m.cargo.toLowerCase().includes(search);
    const matchArea = area === "ALL" || m.area === area;
    const matchRole = role === "ALL" || m.role === role;
    return matchSearch && matchArea && matchRole;
  });

  renderMembersTable(filtered);
}

function openMemberModal(memberId = null) {
  state.currentEditingMemberId = memberId;
  const modal = document.getElementById("modal-member");
  const title = document.getElementById("modal-member-title");
  const btnLabel = document.getElementById("modal-member-btn-label");

  if (memberId) {
    const m = state.members.find(u => u.id === memberId);
    if (!m) return;
    title.textContent = "Editar Atribuições do Membro";
    btnLabel.textContent = "Salvar Alterações";

    document.getElementById("member-form-id").value = m.id;
    document.getElementById("member-name").value = m.nome;
    document.getElementById("member-email").value = m.email;
    document.getElementById("member-area").value = m.area;
    document.getElementById("member-role").value = m.role;
    document.getElementById("member-cargo").value = m.cargo;
    document.getElementById("member-costcenter").value = m.cost_center || "Presidência e Gestão Geral";
    document.getElementById("member-turnover").value = m.turnover_cycle || "Ciclo 2026.1";
    document.getElementById("member-password").value = "";
  } else {
    title.textContent = "Cadastrar Novo Membro";
    btnLabel.textContent = "Cadastrar Membro";
    document.getElementById("member-form").reset();
    document.getElementById("member-form-id").value = "";
    document.getElementById("member-turnover").value = "Ciclo 2026.1";
  }

  if (modal) modal.classList.remove("hidden");
}

function closeMemberModal() {
  const modal = document.getElementById("modal-member");
  if (modal) modal.classList.add("hidden");
  state.currentEditingMemberId = null;
}

async function handleMemberSubmit(e) {
  e.preventDefault();

  const id = document.getElementById("member-form-id").value;
  const payload = {
    nome: document.getElementById("member-name").value.trim(),
    email: document.getElementById("member-email").value.trim(),
    area: document.getElementById("member-area").value,
    role: document.getElementById("member-role").value,
    cargo: document.getElementById("member-cargo").value.trim(),
    cost_center: document.getElementById("member-costcenter").value,
    turnover_cycle: document.getElementById("member-turnover").value.trim(),
    password: document.getElementById("member-password").value.trim() || undefined,
    created_by_name: state.user.nome,
    updated_by_name: state.user.nome
  };

  try {
    let res;
    if (id) {
      res = await fetch(`/api/business/members/${id}`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
      });
    } else {
      res = await fetch("/api/business/members", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
      });
    }

    if (!res.ok) throw new Error("Erro ao salvar cadastro do membro");

    alert(id ? "Atribuições do membro atualizadas com sucesso!" : "Novo membro integrado ao time com sucesso!");
    closeMemberModal();

    // Recarregar dados
    const [memRes, actRes] = await Promise.all([
      fetch("/api/business/members").then(r => r.json()),
      fetch("/api/business/activities").then(r => r.json())
    ]);
    state.members = memRes.members || [];
    state.activities = actRes.activities || [];
    renderMembersTable();
    renderActivityFeed();
  } catch (err) {
    alert("Erro ao salvar membro: " + err.message);
  }
}

async function deleteMember(memberId, memberName) {
  if (!confirm(`Confirma o registro de turnover e desligamento de ${memberName}? O registro será preservado para conformidade estatutária.`)) {
    return;
  }

  try {
    const res = await fetch(`/api/business/members/${memberId}?deleted_by=${encodeURIComponent(state.user.nome)}`, {
      method: "DELETE"
    });
    if (!res.ok) throw new Error("Erro ao registrar desligamento");

    alert(`Turnover registrado com sucesso para ${memberName}.`);
    const [memRes, actRes] = await Promise.all([
      fetch("/api/business/members").then(r => r.json()),
      fetch("/api/business/activities").then(r => r.json())
    ]);
    state.members = memRes.members || [];
    state.activities = actRes.activities || [];
    renderMembersTable();
    renderActivityFeed();
  } catch (err) {
    alert("Erro: " + err.message);
  }
}

async function toggleMemberStatus(memberId) {
  try {
    const res = await fetch(`/api/business/members/${memberId}/toggle-status`, {
      method: "PATCH"
    });
    if (!res.ok) throw new Error("Erro ao alternar status do membro");

    const data = await res.json();
    const newStatus = data.member?.status || "alterado";
    alert(`Status do membro alterado para: ${newStatus.toUpperCase()}`);

    const [memRes, actRes] = await Promise.all([
      fetch("/api/business/members").then(r => r.json()),
      fetch("/api/business/activities").then(r => r.json())
    ]);
    state.members = memRes.members || [];
    state.activities = actRes.activities || [];
    renderMembersTable();
    renderActivityFeed();
  } catch (err) {
    alert("Erro: " + err.message);
  }
}

// ==============================================================================
// 4. EXPORTAÇÃO REAL DE RELATÓRIOS (EXCEL E PDF)
// ==============================================================================
function exportDREExcel() {
  window.open("/api/business/reports/dre/excel", "_blank");
}

function exportDREPDF() {
  window.open("/api/business/reports/dre/pdf-view", "_blank");
}

function exportTimesheetExcel() {
  window.open("/api/business/reports/timesheet/excel", "_blank");
}

// ==============================================================================
// 5. MÓDULO CPQ & PIPELINE COMERCIAL
// ==============================================================================
function populateCPQServicesDropdown() {
  const select = document.getElementById("cpq-service-select");
  if (!select) return;

  select.innerHTML = state.services.map(s => `
    <option value="${s.id}" data-area="${s.macro_area}">
      [${s.code}] ${s.name} (${s.macro_area}) - Lead time: ${s.lead_time_min_weeks}-${s.lead_time_max_weeks} sem
    </option>
  `).join("");

  onCPQServiceChange();
}

function filterServicesArea(area) {
  const select = document.getElementById("cpq-service-select");
  if (!select) return;

  const filtered = area === "ALL" ? state.services : state.services.filter(s => s.macro_area === area);
  select.innerHTML = filtered.map(s => `
    <option value="${s.id}">
      [${s.code}] ${s.name} - Lead time: ${s.lead_time_min_weeks}-${s.lead_time_max_weeks} sem
    </option>
  `).join("");

  onCPQServiceChange();
}

function onCPQServiceChange() {
  const select = document.getElementById("cpq-service-select");
  if (!select) return;

  const serviceId = parseInt(select.value);
  const service = state.services.find(s => s.id === serviceId);

  if (service) {
    const descEl = document.getElementById("cpq-service-desc");
    if (descEl) descEl.textContent = `${service.description} | Entregáveis: ${service.deliverables}`;

    const diagInput = document.getElementById("cpq-horas-diag");
    const execInput = document.getElementById("cpq-horas-exec");
    if (diagInput && execInput) {
      diagInput.value = Math.round(service.default_hh * 0.25);
      execInput.value = Math.round(service.default_hh * 0.75);
    }

    const senSelect = document.getElementById("cpq-seniority-select");
    if (senSelect && service.recommended_seniority) {
      senSelect.value = service.recommended_seniority;
    }
  }

  runCPQSimulation();
}

function onCPQRiskSliderChange() {
  const slider = document.getElementById("cpq-risk-slider");
  const label = document.getElementById("cpq-risk-label");
  if (slider && label) {
    const pct = Math.round((parseFloat(slider.value) - 1.0) * 100);
    label.textContent = `${parseFloat(slider.value).toFixed(2)}x (+${pct}%)`;
  }
  runCPQSimulation();
}

async function runCPQSimulation() {
  const select = document.getElementById("cpq-service-select");
  if (!select || !select.value) return;

  const serviceId = parseInt(select.value);
  const horasDiag = parseInt(document.getElementById("cpq-horas-diag")?.value || 20);
  const horasExec = parseInt(document.getElementById("cpq-horas-exec")?.value || 80);
  const seniority = document.getElementById("cpq-seniority-select")?.value || "Gerente de Projetos";
  const riskFactor = parseFloat(document.getElementById("cpq-risk-slider")?.value || 1.15);

  try {
    const res = await fetch("/api/business/cpq/calculate", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        service_id: serviceId,
        horas_diagnostico: horasDiag,
        horas_execucao: horasExec,
        seniority: seniority,
        risk_factor: riskFactor
      })
    });
    const quote = await res.json();

    document.getElementById("cpq-res-total-hh").textContent = `${quote.total_hh} h`;
    document.getElementById("cpq-res-hourly-rate").textContent = formatCurrency(quote.hourly_rate) + " / h";
    document.getElementById("cpq-res-custo-base").textContent = formatCurrency(quote.custo_base);
    document.getElementById("cpq-res-risco").textContent = `${quote.risk_multiplier.toFixed(2)}x`;
    document.getElementById("cpq-res-reinvestimento").textContent = formatCurrency(quote.fundo_reinvestimento_estatutario);
    document.getElementById("cpq-res-preco-final").textContent = formatCurrency(quote.preco_sugerido);
  } catch (err) {
    console.error("[Nexus Jr.] Erro ao calcular CPQ:", err);
  }
}

async function saveCPQProposal() {
  const select = document.getElementById("cpq-service-select");
  const clientInput = document.getElementById("cpq-client-name");
  const client = clientInput?.value.trim();

  if (!client) {
    alert("Por favor, preencha o Nome do Cliente ou Empresa para gerar a proposta.");
    clientInput?.focus();
    return;
  }

  const payload = {
    service_id: parseInt(select.value),
    client_name: client,
    client_contact: document.getElementById("cpq-client-contact")?.value || "",
    horas_diagnostico: parseInt(document.getElementById("cpq-horas-diag")?.value || 20),
    horas_execucao: parseInt(document.getElementById("cpq-horas-exec")?.value || 80),
    seniority: document.getElementById("cpq-seniority-select")?.value || "Gerente de Projetos",
    risk_factor: parseFloat(document.getElementById("cpq-risk-slider")?.value || 1.15),
    notes: document.getElementById("cpq-notes")?.value || "",
    created_by: state.user.nome
  };

  try {
    const res = await fetch("/api/business/cpq/save", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    });
    const data = await res.json();

    alert(`Proposta #${data.id} gerada com sucesso para ${data.client_name} no valor de ${formatCurrency(data.total_price)}!`);
    clientInput.value = "";
    
    // Atualizar propostas e atividades
    const [propRes, actRes] = await Promise.all([
      fetch("/api/business/cpq/proposals").then(r => r.json()),
      fetch("/api/business/activities").then(r => r.json())
    ]);
    state.proposals = propRes.proposals || [];
    state.activities = actRes.activities || [];
    renderCPQProposalsTable();
    renderActivityFeed();
  } catch (err) {
    alert("Erro ao salvar proposta comercial: " + err.message);
  }
}

function renderCPQView() {
  renderCPQProposalsTable();
  runCPQSimulation();
}

function renderCPQProposalsTable() {
  const tbody = document.getElementById("cpq-proposals-tbody");
  if (!tbody) return;

  if (state.proposals.length === 0) {
    tbody.innerHTML = `<tr><td colspan="8" class="py-6 text-center text-slate-500 text-xs">Nenhuma proposta cadastrada ainda. Utilize o formulário acima para gerar a primeira cotação.</td></tr>`;
    return;
  }

  const statusMap = {
    proposta_gerada: { label: "Gerada", badge: "badge-active" },
    em_negociacao: { label: "Em Negociação", badge: "badge-mentor" },
    convertida: { label: "Convertida", badge: "badge-approved" },
    perdida: { label: "Perdida", badge: "badge-alert" }
  };

  tbody.innerHTML = state.proposals.map(p => {
    const curStatus = p.status || "proposta_gerada";

    return `
      <tr class="hover:bg-slate-50 transition-colors">
        <td class="py-3 px-4 font-mono font-bold text-slate-800">#${p.id}</td>
        <td class="py-3 px-4 font-medium text-slate-900">
          ${p.client_name}
          ${p.client_contact ? `<div class="text-[11px] text-slate-400 font-mono">${p.client_contact}</div>` : ""}
        </td>
        <td class="py-3 px-4 text-xs">
          <span class="font-semibold text-slate-800">${p.service_name}</span>
          <div class="text-[11px] text-slate-500">${p.macro_area}</div>
        </td>
        <td class="py-3 px-4 text-xs font-mono">${p.total_hh} h</td>
        <td class="py-3 px-4 text-xs font-mono text-emerald-700 font-bold">${formatCurrency(p.statutory_reinvestment)}</td>
        <td class="py-3 px-4 text-xs font-mono font-black text-slate-900">${formatCurrency(p.total_price)}</td>
        <td class="py-3 px-4 whitespace-nowrap">
          <select onchange="changeProposalStatus(${p.id}, this.value)" class="text-[11px] font-semibold rounded p-1 border border-slate-200 bg-white shadow-sm cursor-pointer">
            <option value="proposta_gerada" ${curStatus === 'proposta_gerada' ? 'selected' : ''}>📄 Gerada</option>
            <option value="em_negociacao" ${curStatus === 'em_negociacao' ? 'selected' : ''}>🤝 Negociação</option>
            <option value="convertida" ${curStatus === 'convertida' ? 'selected' : ''}>✅ Convertida</option>
            <option value="perdida" ${curStatus === 'perdida' ? 'selected' : ''}>❌ Perdida</option>
          </select>
        </td>
        <td class="py-3 px-4 text-right whitespace-nowrap">
          <div class="flex items-center justify-end gap-1.5">
            <button onclick="openProposalModal(${p.id})" class="text-slate-600 hover:text-emerald-700 p-1.5 rounded hover:bg-slate-100 transition" title="Editar Proposta">
              <i class="fa-solid fa-pen-to-square text-xs"></i>
            </button>
            <button onclick="deleteProposal(${p.id}, '${escapeHtml(p.client_name)}')" class="text-slate-400 hover:text-rose-600 p-1.5 rounded hover:bg-rose-50 transition" title="Excluir Proposta">
              <i class="fa-solid fa-trash-can text-xs"></i>
            </button>
          </div>
        </td>
      </tr>
    `;
  }).join("");
}

function openProposalModal(proposalId) {
  const p = state.proposals.find(item => item.id === proposalId);
  if (!p) return;

  document.getElementById("edit-proposal-id").value = p.id;
  document.getElementById("edit-proposal-client").value = p.client_name || "";
  document.getElementById("edit-proposal-contact").value = p.client_contact || "";
  document.getElementById("edit-proposal-status").value = p.status || "proposta_gerada";
  document.getElementById("edit-proposal-seniority").value = p.seniority_level || "Gerente de Projetos";
  document.getElementById("edit-proposal-diag").value = p.horas_diagnostico || 20;
  document.getElementById("edit-proposal-exec").value = p.horas_execucao || 80;
  document.getElementById("edit-proposal-price").value = p.total_price || 0;
  document.getElementById("edit-proposal-notes").value = p.notes || "";

  const modal = document.getElementById("modal-proposal-edit");
  if (modal) modal.classList.remove("hidden");
}

function closeProposalModal() {
  const modal = document.getElementById("modal-proposal-edit");
  if (modal) modal.classList.add("hidden");
}

async function handleProposalEditSubmit(e) {
  e.preventDefault();
  const id = parseInt(document.getElementById("edit-proposal-id").value);
  const diag = parseInt(document.getElementById("edit-proposal-diag").value) || 0;
  const exec = parseInt(document.getElementById("edit-proposal-exec").value) || 0;
  const price = parseFloat(document.getElementById("edit-proposal-price").value) || 0;

  const payload = {
    client_name: document.getElementById("edit-proposal-client").value.trim(),
    client_contact: document.getElementById("edit-proposal-contact").value.trim(),
    status: document.getElementById("edit-proposal-status").value,
    seniority_level: document.getElementById("edit-proposal-seniority").value,
    horas_diagnostico: diag,
    horas_execucao: exec,
    total_hh: diag + exec,
    total_price: price,
    notes: document.getElementById("edit-proposal-notes").value.trim(),
    updated_by: state.user.nome
  };

  try {
    const res = await fetch(`/api/business/cpq/proposals/${id}`, {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    });
    if (!res.ok) throw new Error("Erro ao atualizar proposta");

    alert(`Proposta #${id} atualizada com sucesso!`);
    closeProposalModal();
    await reloadProposalsAndActivities();
  } catch (err) {
    alert("Erro: " + err.message);
  }
}

async function changeProposalStatus(proposalId, newStatus) {
  try {
    const res = await fetch(`/api/business/cpq/proposals/${proposalId}/status`, {
      method: "PATCH",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        status: newStatus,
        updated_by: state.user.nome
      })
    });
    if (!res.ok) throw new Error("Erro ao atualizar status");

    await reloadProposalsAndActivities();
  } catch (err) {
    alert("Erro: " + err.message);
  }
}

async function deleteProposal(proposalId, clientName) {
  if (!confirm(`Confirma a exclusão da proposta comercial #${proposalId} para ${clientName}?`)) {
    return;
  }

  try {
    const res = await fetch(`/api/business/cpq/proposals/${proposalId}?deleted_by=${encodeURIComponent(state.user.nome)}`, {
      method: "DELETE"
    });
    if (!res.ok) throw new Error("Erro ao excluir proposta");

    alert(`Proposta #${proposalId} removida com sucesso.`);
    await reloadProposalsAndActivities();
  } catch (err) {
    alert("Erro: " + err.message);
  }
}

async function reloadProposalsAndActivities() {
  const [propRes, actRes, kpiRes] = await Promise.all([
    fetch("/api/business/cpq/proposals").then(r => r.json()),
    fetch("/api/business/activities").then(r => r.json()),
    fetch("/api/business/kpis/overview").then(r => r.json())
  ]);
  state.proposals = propRes.proposals || [];
  state.activities = actRes.activities || [];
  state.kpis = kpiRes;
  renderCPQProposalsTable();
  renderActivityFeed();
  updateKPIDashboard(kpiRes);
}

// ==============================================================================
// 6. MÓDULO GANTT & TRAVAS DE MENTORES ACADÊMICOS
// ==============================================================================
function renderProjectsGantt() {
  const container = document.getElementById("gantt-projects-container");
  if (!container) return;

  if (state.projects.length === 0) {
    container.innerHTML = `
      <div class="glass-card rounded-xl p-8 text-center text-slate-500 text-sm">
        Nenhum projeto ou contrato ativo cadastrado. Clique em <strong>"+ Novo Projeto / Contrato"</strong> acima para iniciar.
      </div>
    `;
    return;
  }

  container.innerHTML = state.projects.map(p => {
    const milestones = p.milestones || [];
    const hasScopeAlert = p.scope_creep_alert;

    return `
      <div class="glass-card rounded-xl p-6 space-y-4">
        <div class="flex flex-col md:flex-row md:items-center justify-between gap-3 border-b pb-4">
          <div>
            <div class="flex items-center gap-2">
              <span class="text-xs font-bold text-emerald-700 uppercase tracking-wide">${p.macro_area}</span>
              <span class="text-xs bg-slate-100 text-slate-600 px-2 py-0.5 rounded font-mono">Lead Time: ${p.lead_time_weeks} sem</span>
              ${hasScopeAlert ? `<span class="badge-alert"><i class="fa-solid fa-triangle-exclamation mr-1"></i>Alerta Escopo ≥75%</span>` : ""}
            </div>
            <h4 class="text-lg font-bold text-slate-900 mt-1">${p.name}</h4>
            <p class="text-xs text-slate-500">Cliente: <strong>${p.client_name}</strong> &bull; Gerente: ${p.manager_name} &bull; Período: ${p.start_date || 'A definir'} a ${p.expected_end_date || 'A definir'}</p>
          </div>

          <div class="flex items-center gap-4">
            <div class="text-right hidden sm:block">
              <span class="text-xs text-slate-500 font-medium">Esforço Total</span>
              <p class="text-base font-bold font-mono text-slate-800">${p.consumed_hh} h / ${p.total_budgeted_hh} h</p>
            </div>
            <div class="text-right">
              <span class="text-xs text-slate-500 font-medium">Progresso</span>
              <p class="text-base font-black font-mono text-emerald-600">${p.progress_pct}%</p>
            </div>
            <div class="flex items-center gap-1.5 border-l pl-3 ml-2">
              <button onclick="openMilestoneModal(${p.id})" class="btn-primary text-xs py-1.5 px-2.5 flex items-center gap-1 shadow-sm" title="Adicionar Novo Marco ao Cronograma">
                <i class="fa-solid fa-plus text-xs"></i>
                <span class="hidden sm:inline">Marco</span>
              </button>
              <button onclick="openProjectModal(${p.id})" class="text-slate-600 hover:text-emerald-700 p-2 rounded hover:bg-slate-100 transition" title="Editar Dados do Projeto">
                <i class="fa-solid fa-pen-to-square text-xs"></i>
              </button>
              <button onclick="deleteProject(${p.id}, '${escapeHtml(p.name)}')" class="text-slate-400 hover:text-rose-600 p-2 rounded hover:bg-rose-50 transition" title="Excluir Projeto">
                <i class="fa-solid fa-trash-can text-xs"></i>
              </button>
            </div>
          </div>
        </div>

        <div class="w-full bg-slate-200 rounded-full h-3 overflow-hidden">
          <div class="bg-gradient-to-r from-emerald-600 to-emerald-400 h-3 rounded-full" style="width: ${p.progress_pct}%"></div>
        </div>

        <div class="mt-4 overflow-x-auto">
          <table class="w-full text-left text-xs">
            <thead class="bg-slate-50 text-slate-600 font-bold uppercase tracking-wider border-y">
              <tr>
                <th class="py-2.5 px-3">Fase / Marco Técnico</th>
                <th class="py-2.5 px-3">Cronograma</th>
                <th class="py-2.5 px-3">Consumo HH</th>
                <th class="py-2.5 px-3">Avanço</th>
                <th class="py-2.5 px-3">Caminho Crítico</th>
                <th class="py-2.5 px-3">Chancela Mentor / Trava</th>
                <th class="py-2.5 px-3 text-right">Ações</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-slate-100 font-medium">
              ${milestones.map(m => {
                const isApproved = m.mentor_approval_status === "aprovado";
                const isCritical = m.is_critical_path;
                const ratio = m.budgeted_hh > 0 ? (m.consumed_hh / m.budgeted_hh) : 0;
                const scopeAlert = ratio >= 0.75 && m.progress_pct < 90.0;
                const mTitle = m.title || m.phase_name || "Marco";

                return `
                  <tr class="hover:bg-slate-50/80 transition-colors">
                    <td class="py-3 px-3">
                      <div class="font-bold text-slate-900">${mTitle}</div>
                      ${m.description ? `<div class="text-[11px] text-slate-500">${m.description}</div>` : ""}
                    </td>
                    <td class="py-3 px-3 font-mono text-slate-600 whitespace-nowrap">
                      Sem ${m.week_start} &rarr; Sem ${m.week_end}
                    </td>
                    <td class="py-3 px-3 font-mono whitespace-nowrap">
                      <span class="${scopeAlert ? 'text-amber-600 font-black' : 'text-slate-800 font-bold'}">${m.consumed_hh} h</span> / ${m.budgeted_hh} h
                      ${scopeAlert ? `<span class="text-[10px] text-amber-600 font-bold block">(${Math.round(ratio*100)}%)</span>` : ''}
                    </td>
                    <td class="py-3 px-3 whitespace-nowrap">
                      <span class="font-bold text-slate-800">${m.progress_pct}%</span>
                      <div class="w-16 bg-slate-200 rounded-full h-1.5 mt-1 overflow-hidden">
                        <div class="bg-emerald-600 h-1.5" style="width: ${m.progress_pct}%"></div>
                      </div>
                    </td>
                    <td class="py-3 px-3 whitespace-nowrap">
                      ${isCritical ? `<span class="badge-critical"><i class="fa-solid fa-fire text-[10px] mr-1"></i>Crítico</span>` : `<span class="text-slate-400">Regular</span>`}
                    </td>
                    <td class="py-3 px-3 whitespace-nowrap">
                      ${!m.requires_mentor_approval ? `
                        <span class="text-slate-400 text-[11px]">Não exigida</span>
                      ` : isApproved ? `
                        <span class="badge-approved" title="${m.mentor_name} - ${m.mentor_notes || ''}">
                          <i class="fa-solid fa-circle-check mr-1"></i>Chancelado: ${m.mentor_name?.split(' ')[0]}
                        </span>
                      ` : `
                        <span class="badge-mentor">
                          <i class="fa-solid fa-lock mr-1"></i>Trava Ativa: Pendente
                        </span>
                      `}
                    </td>
                    <td class="py-3 px-3 text-right whitespace-nowrap">
                      <div class="flex items-center justify-end gap-1.5">
                        ${m.requires_mentor_approval && !isApproved ? `
                          <button onclick="openMentorModal(${m.id}, '${escapeHtml(mTitle)}', '${escapeHtml(p.name)}')" class="btn-primary text-[11px] py-1 px-2 flex items-center gap-1 shadow-sm">
                            <i class="fa-solid fa-signature"></i>
                            <span>Aprovar</span>
                          </button>
                        ` : ''}
                        <button onclick="openMilestoneModal(${p.id}, ${m.id})" class="text-slate-600 hover:text-emerald-700 p-1.5 rounded hover:bg-slate-100 transition" title="Editar Marco">
                          <i class="fa-solid fa-pen-to-square text-xs"></i>
                        </button>
                        <button onclick="deleteMilestone(${m.id}, '${escapeHtml(mTitle)}')" class="text-slate-400 hover:text-rose-600 p-1.5 rounded hover:bg-rose-50 transition" title="Excluir Marco">
                          <i class="fa-solid fa-trash-can text-xs"></i>
                        </button>
                      </div>
                    </td>
                  </tr>
                `;
              }).join("")}
            </tbody>
          </table>
        </div>
      </div>
    `;
  }).join("");
}

function openMentorModal(milestoneId, milestoneTitle, projectName) {
  state.selectedMilestoneForMentor = milestoneId;
  const modal = document.getElementById("modal-mentor");
  const mTitle = document.getElementById("mentor-modal-milestone-title");
  const pTitle = document.getElementById("mentor-modal-project-title");
  const nameInput = document.getElementById("mentor-name-input");
  const notesInput = document.getElementById("mentor-notes-input");

  if (mTitle) mTitle.textContent = milestoneTitle;
  if (pTitle) pTitle.textContent = projectName;
  if (nameInput) nameInput.value = "Prof. Dr. Marcos Silveira (Orientador)";
  if (notesInput) notesInput.value = "Premissas técnicas revisadas e entregável formalmente chancelado pelo corpo acadêmico.";
  if (modal) modal.classList.remove("hidden");
}

function closeMentorModal() {
  const modal = document.getElementById("modal-mentor");
  if (modal) modal.classList.add("hidden");
  state.selectedMilestoneForMentor = null;
}

async function submitMentorApproval() {
  if (!state.selectedMilestoneForMentor) return;

  const mentorName = document.getElementById("mentor-name-input")?.value.trim();
  const rubric = document.getElementById("mentor-rubric-input")?.value.trim() || "APROVADO-MEJ-2026";
  const notes = document.getElementById("mentor-notes-input")?.value.trim() || "";

  if (!mentorName) {
    alert("O nome do professor ou mentor técnico é obrigatório.");
    return;
  }

  try {
    const res = await fetch(`/api/business/projects/milestones/${state.selectedMilestoneForMentor}/approve-mentor`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        mentor_name: mentorName,
        mentor_rubric: rubric,
        mentor_notes: notes
      })
    });
    const data = await res.json();
    alert(data.message || "Entrega validada pelo mentor!");
    closeMentorModal();
    await reloadProjectsData();
  } catch (err) {
    alert("Erro ao validar aprovação do mentor: " + err.message);
  }
}

function onProjectServiceSelectChange() {
  const sel = document.getElementById("project-service-select");
  if (!sel) return;
  const opt = sel.options[sel.selectedIndex];
  if (!opt) return;

  const area = opt.getAttribute("data-area");
  const lead = opt.getAttribute("data-lead");
  const hh = opt.getAttribute("data-hh");
  const val = opt.getAttribute("data-val");

  if (area) {
    const areaEl = document.getElementById("project-macro-area");
    if (areaEl) areaEl.value = area;
  }
  if (lead) {
    const leadEl = document.getElementById("project-lead-time");
    if (leadEl) leadEl.value = lead;
  }
  if (hh) {
    const hhEl = document.getElementById("project-total-hh");
    if (hhEl) hhEl.value = hh;
  }
  if (val) {
    const valEl = document.getElementById("project-contract-val");
    if (valEl) valEl.value = val;
  }
}

function openProjectModal(projectId = null) {
  const modal = document.getElementById("modal-project");
  const title = document.getElementById("modal-project-title");
  const btnLabel = document.getElementById("modal-project-btn-label");

  if (projectId) {
    const p = state.projects.find(item => item.id === projectId);
    if (!p) return;
    title.textContent = "Editar Projeto / Contrato";
    btnLabel.textContent = "Salvar Alterações";

    document.getElementById("project-form-id").value = p.id;
    document.getElementById("project-name").value = p.name;
    document.getElementById("project-client").value = p.client_name;
    document.getElementById("project-manager").value = p.manager_name;

    const svcEl = document.getElementById("project-service-select");
    if (svcEl && p.service_name) svcEl.value = p.service_name;

    document.getElementById("project-macro-area").value = p.macro_area || "Finanças e Contabilidade";
    document.getElementById("project-status").value = p.status || "em_andamento";
    document.getElementById("project-lead-time").value = p.lead_time_weeks || 10;
    document.getElementById("project-total-hh").value = p.total_budgeted_hh || 100;
    document.getElementById("project-contract-val").value = p.contract_value || 14500;
    document.getElementById("project-start-date").value = p.start_date || "";
    document.getElementById("project-end-date").value = p.expected_end_date || "";
  } else {
    title.textContent = "Novo Projeto / Contrato";
    btnLabel.textContent = "Criar Projeto";
    document.getElementById("project-form").reset();
    document.getElementById("project-form-id").value = "";
    document.getElementById("project-manager").value = state.user.nome;
    onProjectServiceSelectChange();
  }

  if (modal) modal.classList.remove("hidden");
}

function closeProjectModal() {
  const modal = document.getElementById("modal-project");
  if (modal) modal.classList.add("hidden");
}

async function handleProjectSubmit(e) {
  e.preventDefault();
  const id = document.getElementById("project-form-id").value;
  const svcSel = document.getElementById("project-service-select");
  const service_name = svcSel ? svcSel.value : "Consultoria Financeira";

  const payload = {
    name: document.getElementById("project-name").value.trim(),
    client_name: document.getElementById("project-client").value.trim(),
    manager_name: document.getElementById("project-manager").value.trim(),
    service_name: service_name,
    macro_area: document.getElementById("project-macro-area").value,
    status: document.getElementById("project-status").value,
    lead_time_weeks: parseInt(document.getElementById("project-lead-time").value) || 10,
    total_budgeted_hh: parseInt(document.getElementById("project-total-hh").value) || 100,
    contract_value: parseFloat(document.getElementById("project-contract-val").value) || 0,
    start_date: document.getElementById("project-start-date").value || null,
    expected_end_date: document.getElementById("project-end-date").value || null,
    updated_by: state.user.nome
  };

  try {
    let res;
    if (id) {
      res = await fetch(`/api/business/projects/${id}`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
      });
    } else {
      res = await fetch("/api/business/projects", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
      });
    }
    if (!res.ok) throw new Error("Erro ao salvar projeto");

    alert(id ? "Projeto atualizado com sucesso!" : "Novo projeto cadastrado e cronograma inicial criado com sucesso!");
    closeProjectModal();
    await reloadProjectsData();
  } catch (err) {
    alert("Erro: " + err.message);
  }
}

async function deleteProject(projectId, projectName) {
  if (!confirm(`Tem certeza que deseja excluir o projeto "${projectName}" e todos os seus marcos associados?`)) {
    return;
  }

  try {
    const res = await fetch(`/api/business/projects/${projectId}?deleted_by=${encodeURIComponent(state.user.nome)}`, {
      method: "DELETE"
    });
    if (!res.ok) throw new Error("Erro ao excluir projeto");

    alert(`Projeto "${projectName}" excluído com sucesso.`);
    await reloadProjectsData();
  } catch (err) {
    alert("Erro: " + err.message);
  }
}

function openMilestoneModal(projectId, milestoneId = null) {
  document.getElementById("milestone-project-id").value = projectId;
  document.getElementById("milestone-id").value = milestoneId || "";

  const modal = document.getElementById("modal-milestone");
  const title = document.getElementById("modal-milestone-title");
  const btnLabel = document.getElementById("modal-milestone-btn-label");

  if (milestoneId) {
    const project = state.projects.find(p => p.id === projectId);
    const m = project?.milestones?.find(item => item.id === milestoneId);
    if (!m) return;

    title.textContent = "Editar Marco / Fase Técnica";
    btnLabel.textContent = "Salvar Marco";

    document.getElementById("milestone-name").value = m.title || m.phase_name || "";
    document.getElementById("milestone-week-start").value = m.week_start || 1;
    document.getElementById("milestone-week-end").value = m.week_end || 2;
    document.getElementById("milestone-budgeted-hh").value = m.budgeted_hh || 20;
    document.getElementById("milestone-progress-pct").value = m.progress_pct || 0;
    document.getElementById("milestone-critical-path").checked = !!m.is_critical_path;
    document.getElementById("milestone-mentor-req").checked = !!m.requires_mentor_approval;
  } else {
    title.textContent = "Novo Marco / Fase Técnica";
    btnLabel.textContent = "Criar Marco";
    document.getElementById("milestone-form").reset();
    document.getElementById("milestone-project-id").value = projectId;
    document.getElementById("milestone-id").value = "";
  }

  if (modal) modal.classList.remove("hidden");
}

function closeMilestoneModal() {
  const modal = document.getElementById("modal-milestone");
  if (modal) modal.classList.add("hidden");
}

async function handleMilestoneSubmit(e) {
  e.preventDefault();
  const projectId = parseInt(document.getElementById("milestone-project-id").value);
  const milestoneId = document.getElementById("milestone-id").value;

  const payload = {
    phase_name: document.getElementById("milestone-name").value.trim(),
    week_start: parseInt(document.getElementById("milestone-week-start").value) || 1,
    week_end: parseInt(document.getElementById("milestone-week-end").value) || 2,
    budgeted_hh: parseInt(document.getElementById("milestone-budgeted-hh").value) || 20,
    progress_pct: parseFloat(document.getElementById("milestone-progress-pct").value) || 0,
    is_critical_path: document.getElementById("milestone-critical-path").checked,
    requires_mentor_approval: document.getElementById("milestone-mentor-req").checked,
    updated_by: state.user.nome
  };

  try {
    let res;
    if (milestoneId) {
      res = await fetch(`/api/business/projects/milestones/${milestoneId}`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
      });
    } else {
      res = await fetch(`/api/business/projects/${projectId}/milestones`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
      });
    }
    if (!res.ok) throw new Error("Erro ao salvar marco");

    alert(milestoneId ? "Marco atualizado com sucesso!" : "Novo marco inserido no cronograma!");
    closeMilestoneModal();
    await reloadProjectsData();
  } catch (err) {
    alert("Erro: " + err.message);
  }
}

async function deleteMilestone(milestoneId, milestoneName) {
  if (!confirm(`Deseja remover o marco "${milestoneName}"?`)) {
    return;
  }

  try {
    const res = await fetch(`/api/business/projects/milestones/${milestoneId}?deleted_by=${encodeURIComponent(state.user.nome)}`, {
      method: "DELETE"
    });
    if (!res.ok) throw new Error("Erro ao remover marco");

    alert(`Marco "${milestoneName}" removido com sucesso.`);
    await reloadProjectsData();
  } catch (err) {
    alert("Erro: " + err.message);
  }
}

async function reloadProjectsData() {
  const [projRes, dreRes, kpiRes, actRes] = await Promise.all([
    fetch("/api/business/projects/gantt").then(r => r.json()),
    fetch("/api/business/finance/dre-by-project").then(r => r.json()),
    fetch("/api/business/kpis/overview").then(r => r.json()),
    fetch("/api/business/activities").then(r => r.json())
  ]);
  state.projects = projRes.projects || [];
  state.dre = dreRes;
  state.kpis = kpiRes;
  state.activities = actRes.activities || [];

  renderProjectsGantt();
  renderDashboard();
  renderActivityFeed();
  populateTimesheetProjects();
  populateDREFilterDropdown();
  renderDRETable();
  updateKPIDashboard(kpiRes);
}

// ==============================================================================
// 7. MÓDULO REPOSITÓRIO DE ATIVOS INTELECTUAIS (VALUATION/OBZ)
// ==============================================================================
function renderAssets(filteredAssets = null) {
  const container = document.getElementById("assets-grid-container");
  if (!container) return;

  const assetsToRender = filteredAssets || state.assets;

  if (assetsToRender.length === 0) {
    container.innerHTML = `<div class="col-span-3 text-center py-10 text-slate-500 text-xs">Nenhum ativo intelectual encontrado para os filtros selecionados.</div>`;
    return;
  }

  container.innerHTML = assetsToRender.map(a => {
    let iconClass = "fa-file-excel text-emerald-600";
    if (a.file_format === ".bpmn") iconClass = "fa-project-diagram text-blue-600";
    if (a.file_format === ".pdf") iconClass = "fa-file-pdf text-rose-600";
    if (a.file_format === ".docx") iconClass = "fa-file-word text-indigo-600";
    if (a.file_format === ".pptx") iconClass = "fa-file-powerpoint text-amber-600";

    return `
      <div class="glass-card rounded-xl p-5 flex flex-col justify-between space-y-4 hover:border-emerald-500/50 transition-all">
        <div class="space-y-2">
          <div class="flex items-center justify-between">
            <span class="text-[10px] font-bold text-emerald-800 bg-emerald-50 border border-emerald-200 px-2 py-0.5 rounded uppercase">
              ${(a.macro_area || 'Geral').split(' ')[0]}
            </span>
            <div class="flex items-center gap-1.5">
              <span class="badge-turnover">${a.turnover_cycle || '2026.1'}</span>
              <span class="badge-version">${a.version || 'v1.0'}</span>
            </div>
          </div>

          <div class="flex items-start gap-3 pt-1">
            <i class="fa-solid ${iconClass} text-2xl mt-0.5"></i>
            <div>
              <h4 class="text-sm font-bold text-slate-900 leading-snug">${a.title}</h4>
              <p class="text-xs text-slate-500 mt-1 line-clamp-2">${a.version_notes || a.description || 'Modelo de alta precisão calibrado para o MEJ.'}</p>
            </div>
          </div>
        </div>

        <div class="pt-3 border-t border-slate-100 flex items-center justify-between text-xs">
          <span class="text-slate-400 font-mono text-[11px]">${a.author_member || a.author_role || 'Nexus Jr.'}</span>
          <div class="flex items-center gap-1.5">
            <button onclick="openAssetModal(${a.id})" class="text-slate-600 hover:text-emerald-700 p-1.5 rounded hover:bg-slate-100 transition" title="Editar Ativo">
              <i class="fa-solid fa-pen-to-square text-xs"></i>
            </button>
            <button onclick="deleteAsset(${a.id}, '${escapeHtml(a.title)}')" class="text-slate-400 hover:text-rose-600 p-1.5 rounded hover:bg-rose-50 transition" title="Excluir Ativo">
              <i class="fa-solid fa-trash-can text-xs"></i>
            </button>
            <button onclick="simulateAssetDownload('${escapeHtml(a.title)}', '${a.version || 'v1.0'}')" class="text-emerald-700 hover:text-emerald-800 font-semibold flex items-center gap-1 py-1 px-2 rounded bg-emerald-50 hover:bg-emerald-100 transition ml-1">
              <i class="fa-solid fa-download text-xs"></i>
              <span>Baixar</span>
            </button>
          </div>
        </div>
      </div>
    `;
  }).join("");
}

function filterAssets() {
  const search = document.getElementById("assets-search-input")?.value.toLowerCase() || "";
  const area = document.getElementById("assets-area-filter")?.value || "ALL";

  const filtered = state.assets.filter(a => {
    const matchSearch = a.title.toLowerCase().includes(search) || (a.version_notes && a.version_notes.toLowerCase().includes(search)) || (a.description && a.description.toLowerCase().includes(search));
    const matchArea = area === "ALL" || a.macro_area === area;
    return matchSearch && matchArea;
  });

  renderAssets(filtered);
}

function simulateAssetDownload(title, version) {
  alert(`Download do ativo "${title}" (${version}) iniciado com sucesso. Integridade de versionamento preservada contra o turnover!`);
}

function openAssetModal(assetId = null) {
  const modal = document.getElementById("modal-asset");
  const title = document.getElementById("modal-asset-title");
  const btnLabel = document.getElementById("modal-asset-btn-label");

  if (assetId) {
    const a = state.assets.find(item => item.id === assetId);
    if (!a) return;

    title.textContent = "Editar Ativo Intelectual";
    btnLabel.textContent = "Salvar Alterações";

    document.getElementById("asset-form-id").value = a.id;
    document.getElementById("asset-title").value = a.title;
    document.getElementById("asset-macro-area").value = a.macro_area || "Finanças e Contabilidade";
    document.getElementById("asset-format").value = a.file_format || ".xlsx";
    document.getElementById("asset-version").value = a.version || "v1.0";
    document.getElementById("asset-turnover-cycle").value = a.turnover_cycle || "Ciclo 2026.1";
    document.getElementById("asset-url").value = a.download_url || "";
    document.getElementById("asset-author").value = a.author_member || state.user.nome;
    document.getElementById("asset-mentor").value = a.validator_mentor || "";
    document.getElementById("asset-desc").value = a.version_notes || a.description || "";
  } else {
    title.textContent = "Cadastrar Novo Ativo Intelectual";
    btnLabel.textContent = "Publicar Ativo";
    document.getElementById("asset-form").reset();
    document.getElementById("asset-form-id").value = "";
    document.getElementById("asset-author").value = state.user.nome;
    document.getElementById("asset-turnover-cycle").value = "Ciclo 2026.1";
    document.getElementById("asset-version").value = "v1.0";
  }

  if (modal) modal.classList.remove("hidden");
}

function closeAssetModal() {
  const modal = document.getElementById("modal-asset");
  if (modal) modal.classList.add("hidden");
}

async function handleAssetSubmit(e) {
  e.preventDefault();
  const id = document.getElementById("asset-form-id").value;

  const payload = {
    title: document.getElementById("asset-title").value.trim(),
    macro_area: document.getElementById("asset-macro-area").value,
    file_format: document.getElementById("asset-format").value,
    version: document.getElementById("asset-version").value.trim(),
    turnover_cycle: document.getElementById("asset-turnover-cycle").value.trim(),
    download_url: document.getElementById("asset-url").value.trim() || undefined,
    author_member: document.getElementById("asset-author").value.trim(),
    validator_mentor: document.getElementById("asset-mentor").value.trim(),
    version_notes: document.getElementById("asset-desc").value.trim(),
    updated_by: state.user.nome
  };

  try {
    let res;
    if (id) {
      res = await fetch(`/api/business/knowledge/assets/${id}`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
      });
    } else {
      res = await fetch("/api/business/knowledge/assets", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
      });
    }
    if (!res.ok) throw new Error("Erro ao salvar ativo");

    alert(id ? "Ativo intelectual atualizado!" : "Novo ativo publicado com sucesso no repositório!");
    closeAssetModal();

    const [assetsRes, actRes] = await Promise.all([
      fetch("/api/business/knowledge/assets").then(r => r.json()),
      fetch("/api/business/activities").then(r => r.json())
    ]);
    state.assets = assetsRes.assets || [];
    state.activities = actRes.activities || [];
    renderAssets();
    renderActivityFeed();
  } catch (err) {
    alert("Erro: " + err.message);
  }
}

async function deleteAsset(assetId, assetTitle) {
  if (!confirm(`Confirma a remoção do ativo "${assetTitle}" do repositório?`)) {
    return;
  }

  try {
    const res = await fetch(`/api/business/knowledge/assets/${assetId}?deleted_by=${encodeURIComponent(state.user.nome)}`, {
      method: "DELETE"
    });
    if (!res.ok) throw new Error("Erro ao excluir ativo");

    alert(`Ativo "${assetTitle}" removido com sucesso.`);
    const [assetsRes, actRes] = await Promise.all([
      fetch("/api/business/knowledge/assets").then(r => r.json()),
      fetch("/api/business/activities").then(r => r.json())
    ]);
    state.assets = assetsRes.assets || [];
    state.activities = actRes.activities || [];
    renderAssets();
    renderActivityFeed();
  } catch (err) {
    alert("Erro: " + err.message);
  }
}

// ==============================================================================
// 8. MÓDULO TIMESHEET & ALERTA DE SCOPE CREEP
// ==============================================================================
function populateTimesheetProjects() {
  const pSelect = document.getElementById("ts-project-select");
  if (!pSelect) return;

  pSelect.innerHTML = state.projects.map(p => `
    <option value="${p.id}">${p.name} (${p.client_name})</option>
  `).join("");

  onTimesheetProjectChange();
}

function onTimesheetProjectChange() {
  const pSelect = document.getElementById("ts-project-select");
  const mSelect = document.getElementById("ts-milestone-select");
  if (!pSelect || !mSelect) return;

  const projectId = parseInt(pSelect.value);
  const project = state.projects.find(p => p.id === projectId);

  if (project && project.milestones) {
    mSelect.innerHTML = project.milestones.map(m => `
      <option value="${m.id}">[Sem ${m.week_start}-${m.week_end}] ${m.title} (${m.consumed_hh}/${m.budgeted_hh}h)</option>
    `).join("");
  } else {
    mSelect.innerHTML = `<option value="">Nenhum marco cadastrado</option>`;
  }
}

async function handleTimesheetSubmit(e) {
  e.preventDefault();

  const projectId = parseInt(document.getElementById("ts-project-select")?.value);
  const milestoneId = parseInt(document.getElementById("ts-milestone-select")?.value) || null;
  const date = document.getElementById("ts-date")?.value;
  const hours = parseFloat(document.getElementById("ts-hours")?.value);
  const name = document.getElementById("ts-consultant-name")?.value;
  const email = document.getElementById("ts-consultant-email")?.value;
  const desc = document.getElementById("ts-description")?.value;

  if (!projectId || !hours || !desc) {
    alert("Preencha todos os campos obrigatórios.");
    return;
  }

  try {
    const res = await fetch("/api/business/timesheet/log", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        project_id: projectId,
        milestone_id: milestoneId,
        consultant_name: name,
        consultant_email: email,
        date: date,
        hours: hours,
        description: desc
      })
    });
    const data = await res.json();

    if (data.scope_alert_triggered) {
      alert(`⚠️ ALERTA DE SCOPE CREEP: Este lançamento fez o marco ultrapassar 75% das horas orçadas com progresso ainda incompleto! Um alerta foi registrado para a gerência de projetos.`);
    } else {
      alert("Horas apontadas com sucesso no timesheet!");
    }

    document.getElementById("ts-hours").value = "";
    document.getElementById("ts-description").value = "";

    const [tRes, pRes, actRes] = await Promise.all([
      fetch("/api/business/timesheet").then(r => r.json()),
      fetch("/api/business/projects/gantt").then(r => r.json()),
      fetch("/api/business/activities").then(r => r.json())
    ]);
    state.timesheet = tRes.entries || [];
    state.scopeAlerts = tRes.active_scope_alerts || [];
    state.projects = pRes.projects || [];
    state.activities = actRes.activities || [];

    renderTimesheetView();
    renderDashboard();
    renderActivityFeed();
  } catch (err) {
    alert("Erro ao registrar no timesheet: " + err.message);
  }
}

function renderTimesheetView() {
  renderTimesheetAlerts();
  renderTimesheetTable();
}

function renderTimesheetAlerts() {
  const container = document.getElementById("timesheet-scope-alerts");
  if (!container) return;

  if (state.scopeAlerts.length === 0) {
    container.innerHTML = `
      <div class="p-4 bg-emerald-50 border border-emerald-200 rounded-lg text-emerald-800 text-xs flex items-center gap-2">
        <i class="fa-solid fa-circle-check text-emerald-600 text-sm"></i>
        <span>Todos os projetos estão dentro da margem de segurança de horas orçadas. Nenhum estouro de escopo detectado.</span>
      </div>
    `;
    return;
  }

  container.innerHTML = state.scopeAlerts.map(a => `
    <div class="p-4 bg-amber-50 border-l-4 border-amber-500 rounded-r-lg shadow-sm space-y-1">
      <div class="flex items-center justify-between">
        <span class="text-xs font-bold text-amber-900 flex items-center gap-1.5">
          <i class="fa-solid fa-triangle-exclamation text-amber-600"></i>
          Alerta Scope Creep: ${a.project_name}
        </span>
        <span class="text-[11px] bg-amber-200 text-amber-900 font-bold px-2 py-0.5 rounded">
          ${Math.round((a.consumed_hh / a.budgeted_hh) * 100)}% Consumido
        </span>
      </div>
      <p class="text-xs text-amber-800">
        <strong>Fase:</strong> ${a.title} &bull; Horas: <strong>${a.consumed_hh}h de ${a.budgeted_hh}h</strong> orçadas &bull; Avanço atual: <strong>${a.progress_pct}%</strong> (abaixo dos 90% esperados para esta faixa).
      </p>
    </div>
  `).join("");
}

function renderTimesheetTable() {
  const tbody = document.getElementById("timesheet-tbody");
  if (!tbody) return;

  if (state.timesheet.length === 0) {
    tbody.innerHTML = `<tr><td colspan="7" class="py-6 text-center text-slate-500 text-xs">Nenhum apontamento de timesheet registrado.</td></tr>`;
    return;
  }

  tbody.innerHTML = state.timesheet.map(t => `
    <tr class="hover:bg-slate-50 transition-colors">
      <td class="py-3 px-4 font-mono text-xs text-slate-600">${t.date}</td>
      <td class="py-3 px-4 text-xs font-semibold text-slate-800">${t.consultant_name}</td>
      <td class="py-3 px-4 text-xs">
        <div class="font-bold text-slate-800">${t.project_name || 'Projeto #' + t.project_id}</div>
        <div class="text-[11px] text-slate-500">${t.milestone_title || 'Marco Geral'}</div>
      </td>
      <td class="py-3 px-4 font-mono font-bold text-slate-900 text-xs">${t.hours} h</td>
      <td class="py-3 px-4 text-xs text-slate-600 max-w-xs truncate">${t.description}</td>
      <td class="py-3 px-4">
        ${t.scope_alert_triggered ? `<span class="badge-alert"><i class="fa-solid fa-triangle-exclamation mr-1"></i>Scope Alert</span>` : `<span class="text-emerald-600 text-xs font-medium"><i class="fa-solid fa-check mr-1"></i>Normal</span>`}
      </td>
      <td class="py-3 px-4 text-right whitespace-nowrap">
        <div class="flex items-center justify-end gap-1.5">
          <button onclick="openTimesheetEditModal(${t.id})" class="text-slate-600 hover:text-emerald-700 p-1.5 rounded hover:bg-slate-100 transition" title="Editar Lançamento">
            <i class="fa-solid fa-pen-to-square text-xs"></i>
          </button>
          <button onclick="deleteTimesheetEntry(${t.id}, ${t.project_id})" class="text-slate-400 hover:text-rose-600 p-1.5 rounded hover:bg-rose-50 transition" title="Excluir Lançamento">
            <i class="fa-solid fa-trash-can text-xs"></i>
          </button>
        </div>
      </td>
    </tr>
  `).join("");
}

function openTimesheetEditModal(entryId) {
  const t = state.timesheet.find(item => item.id === entryId);
  if (!t) return;

  document.getElementById("ts-edit-id").value = t.id;
  document.getElementById("ts-edit-date").value = t.date;
  document.getElementById("ts-edit-hours").value = t.hours;
  document.getElementById("ts-edit-desc").value = t.description;

  const modal = document.getElementById("modal-timesheet-edit");
  if (modal) modal.classList.remove("hidden");
}

function closeTimesheetEditModal() {
  const modal = document.getElementById("modal-timesheet-edit");
  if (modal) modal.classList.add("hidden");
}

async function handleTimesheetEditSubmit(e) {
  e.preventDefault();
  const id = parseInt(document.getElementById("ts-edit-id").value);
  const date = document.getElementById("ts-edit-date").value;
  const hours = parseFloat(document.getElementById("ts-edit-hours").value);
  const desc = document.getElementById("ts-edit-desc").value.trim();

  if (!id || !hours || !desc) return;

  try {
    const res = await fetch(`/api/business/timesheet/${id}`, {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        date: date,
        hours: hours,
        description: desc,
        updated_by: state.user.nome
      })
    });
    if (!res.ok) throw new Error("Erro ao atualizar apontamento");

    const data = await res.json();
    alert(`Lançamento de horas atualizado! Consumo recalculado com sucesso.`);
    closeTimesheetEditModal();
    await reloadTimesheetData();
  } catch (err) {
    alert("Erro: " + err.message);
  }
}

async function deleteTimesheetEntry(entryId, projectId) {
  if (!confirm(`Confirma a exclusão deste apontamento de horas? As horas serão subtraídas e o consumo recalculado automaticamente.`)) {
    return;
  }

  try {
    const res = await fetch(`/api/business/timesheet/${entryId}?deleted_by=${encodeURIComponent(state.user.nome)}`, {
      method: "DELETE"
    });
    if (!res.ok) throw new Error("Erro ao excluir apontamento");

    alert("Apontamento excluído e horas recalculadas no projeto.");
    await reloadTimesheetData();
  } catch (err) {
    alert("Erro: " + err.message);
  }
}

async function reloadTimesheetData() {
  const [tRes, pRes, actRes, kpiRes] = await Promise.all([
    fetch("/api/business/timesheet").then(r => r.json()),
    fetch("/api/business/projects/gantt").then(r => r.json()),
    fetch("/api/business/activities").then(r => r.json()),
    fetch("/api/business/kpis/overview").then(r => r.json())
  ]);

  state.timesheet = tRes.entries || [];
  state.scopeAlerts = tRes.active_scope_alerts || [];
  state.projects = pRes.projects || [];
  state.activities = actRes.activities || [];
  state.kpis = kpiRes;

  renderTimesheetView();
  renderProjectsGantt();
  renderDashboard();
  renderActivityFeed();
  renderDashboardCharts();
  updateKPIDashboard(kpiRes);
}

// ==============================================================================
// 9. MÓDULO TESOURARIA, COMPLIANCE & DRE GERENCIAL POR CENTRO DE CUSTO
// ==============================================================================
function populateDREFilterDropdown() {
  const filter = document.getElementById("dre-project-filter");
  if (!filter || !state.dre) return;

  const options = [`<option value="CONSOLIDADO">Todos os Projetos (Consolidado)</option>`];
  (state.dre.projetos || []).forEach(p => {
    options.push(`<option value="${p.id}">CC #${p.project_id}: ${p.project_name} (${p.client_name})</option>`);
  });

  filter.innerHTML = options.join("");
}

function renderDRETable() {
  if (!state.dre) return;

  const filter = document.getElementById("dre-project-filter");
  const selected = filter ? filter.value : "CONSOLIDADO";
  const tbody = document.getElementById("dre-table-body");
  const heading = document.getElementById("dre-title-heading");
  const marginList = document.getElementById("dre-margin-list");

  let dreObj = null;
  if (selected === "CONSOLIDADO") {
    if (heading) heading.textContent = "Demonstrativo Consolidado do Exercício (2026)";
    dreObj = {
      receita_bruta: state.dre.consolidado.total_receita_bruta,
      impostos_deducoes: 0.0,
      receita_liquida: state.dre.consolidado.total_receita_bruta,
      custos_diretos_softwares: 2400.0,
      custos_diretos_operacionais: 1050.0,
      custos_diretos_total: state.dre.consolidado.total_custos_diretos,
      margem_contribuicao: state.dre.consolidado.total_margem_contribuicao,
      margem_contribuicao_pct: state.dre.consolidado.margem_contribuicao_media_pct,
      despesas_operacionais_rateadas: state.dre.consolidado.total_despesas_rateadas,
      superavit_liquido: state.dre.consolidado.total_superavit_estatutario,
      reinvestimento_pct: 100.0
    };
  } else {
    const proj = state.dre.projetos.find(p => p.id === parseInt(selected));
    if (proj) {
      if (heading) heading.textContent = `DRE do Centro de Custo: ${proj.project_name}`;
      dreObj = {
        receita_bruta: proj.receita_bruta,
        impostos_deducoes: proj.impostos_deducoes,
        receita_liquida: proj.receita_liquida,
        custos_diretos_softwares: proj.custos_diretos_softwares,
        custos_diretos_operacionais: proj.custos_diretos_operacionais,
        custos_diretos_total: proj.custos_diretos_softwares + proj.custos_diretos_operacionais,
        margem_contribuicao: proj.margem_contribuicao,
        margem_contribuicao_pct: proj.margem_contribuicao_pct,
        despesas_operacionais_rateadas: proj.despesas_operacionais_rateadas,
        superavit_liquido: proj.superavit_liquido,
        reinvestimento_pct: proj.reinvestimento_obrigatorio_pct * 100
      };
    }
  }

  if (tbody && dreObj) {
    tbody.innerHTML = `
      <tr class="font-bold text-slate-900 bg-slate-50">
        <td class="py-3 px-4">(+) RECEITA BRUTA DE CONSULTORIA</td>
        <td class="py-3 px-4 text-right font-mono">${formatCurrency(dreObj.receita_bruta)}</td>
        <td class="py-3 px-4 text-right font-mono text-xs text-slate-500">100.0%</td>
      </tr>
      <tr class="text-slate-600">
        <td class="py-2.5 px-4 pl-8">(-) Deduções e Tributos (Imunidade/Isenção Estatutária)</td>
        <td class="py-2.5 px-4 text-right font-mono text-slate-500">R$ 0,00</td>
        <td class="py-2.5 px-4 text-right font-mono text-xs text-slate-500">0.0%</td>
      </tr>
      <tr class="font-semibold text-slate-800 bg-slate-50/50">
        <td class="py-3 px-4">(=) RECEITA OPERACIONAL LÍQUIDA</td>
        <td class="py-3 px-4 text-right font-mono text-slate-900">${formatCurrency(dreObj.receita_liquida)}</td>
        <td class="py-3 px-4 text-right font-mono text-xs text-slate-500">100.0%</td>
      </tr>
      <tr class="text-rose-700">
        <td class="py-2 px-4 pl-8">(-) Custos Diretos com Licenças e Softwares Especializados</td>
        <td class="py-2 px-4 text-right font-mono">-${formatCurrency(dreObj.custos_diretos_softwares)}</td>
        <td class="py-2 px-4 text-right font-mono text-xs text-rose-600">-${(dreObj.custos_diretos_softwares/dreObj.receita_bruta*100).toFixed(1)}%</td>
      </tr>
      <tr class="text-rose-700">
        <td class="py-2 px-4 pl-8">(-) Custos Operacionais Diretos de Deslocamento/Insumos</td>
        <td class="py-2 px-4 text-right font-mono">-${formatCurrency(dreObj.custos_diretos_operacionais)}</td>
        <td class="py-2 px-4 text-right font-mono text-xs text-rose-600">-${(dreObj.custos_diretos_operacionais/dreObj.receita_bruta*100).toFixed(1)}%</td>
      </tr>
      <tr class="font-bold text-emerald-800 bg-emerald-50 border-y border-emerald-200">
        <td class="py-3 px-4">(=) MARGEM DE CONTRIBUIÇÃO DIRETA</td>
        <td class="py-3 px-4 text-right font-mono text-base">${formatCurrency(dreObj.margem_contribuicao)}</td>
        <td class="py-3 px-4 text-right font-mono text-sm">${dreObj.margem_contribuicao_pct}%</td>
      </tr>
      <tr class="text-slate-600">
        <td class="py-2.5 px-4 pl-8">(-) Despesas Administrativas e Operacionais Rateadas</td>
        <td class="py-2.5 px-4 text-right font-mono text-slate-700">-${formatCurrency(dreObj.despesas_operacionais_rateadas)}</td>
        <td class="py-2.5 px-4 text-right font-mono text-xs text-slate-500">-${(dreObj.despesas_operacionais_rateadas/dreObj.receita_bruta*100).toFixed(1)}%</td>
      </tr>
      <tr class="font-black text-[#0b1d3a] bg-slate-100 text-base border-t-2 border-slate-300">
        <td class="py-4 px-4">(=) SUPERÁVIT LÍQUIDO DO EXERCÍCIO</td>
        <td class="py-4 px-4 text-right font-mono">${formatCurrency(dreObj.superavit_liquido)}</td>
        <td class="py-4 px-4 text-right font-mono text-sm">${(dreObj.superavit_liquido/dreObj.receita_bruta*100).toFixed(1)}%</td>
      </tr>
      <tr class="bg-emerald-100/60 text-emerald-950 font-bold text-xs">
        <td class="py-3 px-4 pl-8 flex items-center gap-1.5">
          <i class="fa-solid fa-arrows-spin"></i> Destinação Estatutária Obrigatória (Lei 13.267) &rarr; Reinvestimento Integral
        </td>
        <td class="py-3 px-4 text-right font-mono font-black">${formatCurrency(dreObj.superavit_liquido)}</td>
        <td class="py-3 px-4 text-right font-mono">100.0%</td>
      </tr>
    `;
  }

  if (marginList && state.dre.projetos) {
    marginList.innerHTML = state.dre.projetos.map(p => `
      <div class="flex items-center justify-between text-xs p-2 rounded hover:bg-slate-50 border border-slate-100">
        <div class="truncate pr-2">
          <span class="font-bold text-slate-800 block truncate">${p.project_name}</span>
          <span class="text-[10px] text-slate-500">${p.client_name}</span>
        </div>
        <div class="text-right flex-shrink-0">
          <span class="font-bold text-emerald-700 font-mono">${p.margem_contribuicao_pct}%</span>
          <span class="text-[10px] text-slate-500 block font-mono">${formatCurrency(p.margem_contribuicao)}</span>
        </div>
      </div>
    `).join("");
  }
}

// ==============================================================================
// 10. MÓDULO FORECASTING PREDITIVO & CENÁRIOS MACROECONÔMICOS (12-36M)
// ==============================================================================

function switchFinanceSubTab(tabName) {
  state.financeSubTab = tabName;
  const btnDRE = document.getElementById("subtab-btn-dre");
  const btnForecasting = document.getElementById("subtab-btn-forecasting");
  const subDRE = document.getElementById("finance-subtab-dre");
  const subForecasting = document.getElementById("finance-subtab-forecasting");

  if (tabName === "dre") {
    if (btnDRE) {
      btnDRE.className = "px-4 py-2 text-xs font-bold rounded-lg transition-all bg-emerald-700 text-white shadow-sm flex items-center gap-2";
    }
    if (btnForecasting) {
      btnForecasting.className = "px-4 py-2 text-xs font-bold rounded-lg transition-all bg-slate-100 text-slate-700 hover:bg-slate-200 flex items-center gap-2";
    }
    if (subDRE) subDRE.classList.remove("hidden");
    if (subForecasting) subForecasting.classList.add("hidden");

    renderDRETable();
    setTimeout(renderDREChart, 50);
  } else {
    if (btnDRE) {
      btnDRE.className = "px-4 py-2 text-xs font-bold rounded-lg transition-all bg-slate-100 text-slate-700 hover:bg-slate-200 flex items-center gap-2";
    }
    if (btnForecasting) {
      btnForecasting.className = "px-4 py-2 text-xs font-bold rounded-lg transition-all bg-emerald-700 text-white shadow-sm flex items-center gap-2";
    }
    if (subDRE) subDRE.classList.add("hidden");
    if (subForecasting) subForecasting.classList.remove("hidden");

    if (!state.forecasting) {
      loadForecastingData();
    } else {
      renderForecastingDashboard(state.forecasting);
      setTimeout(() => renderForecastingCharts(state.forecasting), 50);
      renderForecastingTable();
    }
  }
}

let paramDebounceTimer = null;
function onForecastingParamChange() {
  const gBase = document.getElementById("param-growth-base")?.value || 15;
  const oBonus = document.getElementById("param-opt-bonus")?.value || 20;
  const pPenalty = document.getElementById("param-pess-penalty")?.value || 15;
  const inf = document.getElementById("param-inflation")?.value || 5.5;
  const sIntensity = document.getElementById("param-seasonality")?.value || 1.0;

  const lblGBase = document.getElementById("label-param-growth-base");
  const lblOBonus = document.getElementById("label-param-opt-bonus");
  const lblPPenalty = document.getElementById("label-param-pess-penalty");
  const lblInf = document.getElementById("label-param-inflation");
  const lblSIntensity = document.getElementById("label-param-seasonality");

  if (lblGBase) lblGBase.textContent = `${parseFloat(gBase).toFixed(1)}%`;
  if (lblOBonus) lblOBonus.textContent = `+${parseFloat(oBonus).toFixed(1)}%`;
  if (lblPPenalty) lblPPenalty.textContent = `-${parseFloat(pPenalty).toFixed(1)}%`;
  if (lblInf) lblInf.textContent = `${parseFloat(inf).toFixed(1)}%`;
  if (lblSIntensity) lblSIntensity.textContent = `${parseFloat(sIntensity).toFixed(1)}x`;

  clearTimeout(paramDebounceTimer);
  paramDebounceTimer = setTimeout(() => {
    loadForecastingData();
  }, 250);
}

function resetForecastingParams() {
  const gEl = document.getElementById("param-growth-base");
  const oEl = document.getElementById("param-opt-bonus");
  const pEl = document.getElementById("param-pess-penalty");
  const infEl = document.getElementById("param-inflation");
  const sEl = document.getElementById("param-seasonality");
  const cashEl = document.getElementById("param-initial-cash");

  if (gEl) gEl.value = 15;
  if (oEl) oEl.value = 20;
  if (pEl) pEl.value = 15;
  if (infEl) infEl.value = 5.5;
  if (sEl) sEl.value = 1.0;
  if (cashEl) cashEl.value = 45000;

  onForecastingParamChange();
}

function setForecastHorizon(months) {
  state.forecastHorizon = months;

  [12, 24, 36].forEach(m => {
    const btn = document.getElementById(`btn-horizon-${m}`);
    if (btn) {
      if (m === months) {
        btn.className = "px-3 py-1.5 text-xs font-bold rounded-md transition bg-[#0b1d3a] text-white shadow-xs";
      } else {
        btn.className = "px-3 py-1.5 text-xs font-semibold rounded-md transition text-slate-600 hover:text-slate-900";
      }
    }
  });

  const hLabel = document.getElementById("forecast-horizon-label");
  if (hLabel) hLabel.textContent = `Horizonte: ${months} meses`;

  loadForecastingData();
}

function setForecastChartMetric(metric) {
  state.forecastMetric = metric;

  const metricTitles = {
    saldo_acumulado: "Evolução do Saldo de Caixa Acumulado",
    fluxo_liquido: "Fluxo de Caixa Líquido Mensal",
    receita: "Receita Bruta Mensal de Projetos",
    custos: "Custos Operacionais Mensais"
  };

  const titleEl = document.getElementById("forecast-chart-main-title");
  if (titleEl && metricTitles[metric]) {
    titleEl.textContent = metricTitles[metric];
  }

  const buttons = {
    saldo_acumulado: "metric-btn-saldo",
    fluxo_liquido: "metric-btn-fluxo",
    receita: "metric-btn-receita",
    custos: "metric-btn-custos"
  };

  Object.entries(buttons).forEach(([m, id]) => {
    const btn = document.getElementById(id);
    if (btn) {
      if (m === metric) {
        btn.className = "px-2.5 py-1 font-bold rounded-md transition bg-white text-emerald-800 shadow-xs";
      } else {
        btn.className = "px-2.5 py-1 font-semibold rounded-md transition text-slate-600 hover:text-slate-900";
      }
    }
  });

  if (state.forecasting) {
    renderForecastingCharts(state.forecasting);
  }
}

async function loadForecastingData() {
  const gBase = parseFloat(document.getElementById("param-growth-base")?.value || 15);
  const oBonus = parseFloat(document.getElementById("param-opt-bonus")?.value || 20);
  const pPenalty = parseFloat(document.getElementById("param-pess-penalty")?.value || 15);
  const inf = parseFloat(document.getElementById("param-inflation")?.value || 5.5);
  const sIntensity = parseFloat(document.getElementById("param-seasonality")?.value || 1.0);
  const initialCash = parseFloat(document.getElementById("param-initial-cash")?.value || 45000);

  const payload = {
    horizon_months: state.forecastHorizon || 24,
    growth_rate_annual_pct: gBase,
    optimistic_growth_bonus_pct: oBonus,
    pessimistic_growth_penalty_pct: pPenalty,
    inflation_annual_pct: inf,
    cost_containment_bonus_pct: 5.0,
    pessimistic_inflation_penalty_pct: 6.0,
    seasonality_intensity: sIntensity * 0.25,
    initial_cash_balance: initialCash
  };

  try {
    const res = await fetch("/api/business/finance/forecasting", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    });
    if (!res.ok) throw new Error("Falha ao calcular projeção preditiva");

    const data = await res.json();
    state.forecasting = data;

    renderForecastingDashboard(data);
    renderForecastingCharts(data);
    renderForecastingTable();
  } catch (err) {
    console.error("[Forecasting Error]:", err);
  }
}

function renderForecastingDashboard(data) {
  if (!data || !data.cenarios) return;

  const base = data.cenarios.base?.resumo || {};
  const opt = data.cenarios.otimista?.resumo || {};
  const pess = data.cenarios.pessimista?.resumo || {};
  const prem = data.premissas || {};

  const elSupBase = document.getElementById("kpi-forecast-superavit-base");
  const elSupAlt = document.getElementById("kpi-forecast-superavit-alt");
  const elSaldoFin = document.getElementById("kpi-forecast-saldo-final");
  const elSaldoMin = document.getElementById("kpi-forecast-saldo-min");
  const elBreakEven = document.getElementById("kpi-forecast-breakeven");
  const elContratosBE = document.getElementById("kpi-forecast-contratos-be");
  const elRunway = document.getElementById("kpi-forecast-runway");
  const elProb = document.getElementById("kpi-forecast-prob");
  const elInsight = document.getElementById("forecast-chart-insight");

  if (elSupBase) elSupBase.textContent = formatCurrency(base.superavit_estatutario_total || 0);
  if (elSupAlt) elSupAlt.innerHTML = `Opt: <strong class="text-emerald-700">${formatCurrency(opt.superavit_estatutario_total || 0)}</strong> | Pess: <strong class="text-rose-700">${formatCurrency(pess.superavit_estatutario_total || 0)}</strong>`;
  if (elSaldoFin) elSaldoFin.textContent = formatCurrency(base.saldo_final_tesouraria || 0);
  if (elSaldoMin) elSaldoMin.textContent = formatCurrency(base.saldo_minimo_tesouraria || 0);
  if (elBreakEven) elBreakEven.textContent = `${formatCurrency(base.ponto_equilibrio_mensal || 0)}/mês`;
  if (elContratosBE) elContratosBE.textContent = (base.contratos_breakeven_mes || 0).toFixed(1);
  if (elRunway) elRunway.textContent = `${prem.runway_meses_sem_vendas || 0} meses`;
  if (elProb) elProb.textContent = `${base.probabilidade_superavit_positivo || 100}%`;

  if (elInsight) {
    if (pess.saldo_minimo_tesouraria < 0) {
      elInsight.textContent = `Atenção: No Cenário Pessimista haverá necessidade de contingência de caixa no mês mais crítico.`;
    } else {
      elInsight.textContent = `No Cenário Base (${prem.horizon_months} meses), o superávit estatutário acumulado projetado é de ${formatCurrency(base.superavit_estatutario_total || 0)}, blindado pela Lei nº 13.267/2016.`;
    }
  }
}

function renderForecastingCharts(data) {
  if (!data || !data.cenarios || !data.labels) return;

  // 1. Gráfico Principal de Linhas / Áreas
  const ctxMain = document.getElementById("chart-forecasting-main");
  if (ctxMain) {
    if (state.charts.forecastMain) {
      state.charts.forecastMain.destroy();
    }

    const metric = state.forecastMetric || "saldo_acumulado";
    const labels = data.labels;

    const optVals = data.cenarios.otimista.dados[metric] || [];
    const baseVals = data.cenarios.base.dados[metric] || [];
    const pessVals = data.cenarios.pessimista.dados[metric] || [];

    state.charts.forecastMain = new Chart(ctxMain, {
      type: "line",
      data: {
        labels: labels,
        datasets: [
          {
            label: "Cenário Otimista",
            data: optVals,
            borderColor: "#059669",
            backgroundColor: "rgba(5, 150, 105, 0.08)",
            borderWidth: 2.5,
            fill: true,
            tension: 0.35,
            pointRadius: 2.5,
            pointHoverRadius: 5
          },
          {
            label: "Cenário Base",
            data: baseVals,
            borderColor: "#0b1d3a",
            backgroundColor: "rgba(11, 29, 58, 0.04)",
            borderWidth: 3,
            fill: false,
            tension: 0.35,
            pointRadius: 3,
            pointHoverRadius: 6
          },
          {
            label: "Cenário Pessimista",
            data: pessVals,
            borderColor: "#e11d48",
            backgroundColor: "rgba(225, 29, 72, 0.06)",
            borderWidth: 2,
            borderDash: [5, 4],
            fill: false,
            tension: 0.35,
            pointRadius: 2.5,
            pointHoverRadius: 5
          }
        ]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        interaction: {
          mode: "index",
          intersect: false
        },
        plugins: {
          legend: {
            display: false
          },
          tooltip: {
            callbacks: {
              label: (ctx) => ` ${ctx.dataset.label}: ${formatCurrency(ctx.raw)}`
            }
          }
        },
        scales: {
          y: {
            beginAtZero: false,
            ticks: {
              callback: (val) => "R$ " + (val / 1000).toFixed(0) + "k",
              font: { size: 10 }
            },
            grid: { color: "#f1f5f9" }
          },
          x: {
            grid: { display: false },
            ticks: { font: { size: 10 } }
          }
        }
      }
    });
  }

  // 2. Gráfico Comparativo: Superávit Estatutário Total Acumulado (Barras)
  const ctxComp = document.getElementById("chart-forecasting-comparison");
  if (ctxComp) {
    if (state.charts.forecastComp) {
      state.charts.forecastComp.destroy();
    }

    const optSup = data.cenarios.otimista.resumo.superavit_estatutario_total;
    const baseSup = data.cenarios.base.resumo.superavit_estatutario_total;
    const pessSup = data.cenarios.pessimista.resumo.superavit_estatutario_total;

    state.charts.forecastComp = new Chart(ctxComp, {
      type: "bar",
      data: {
        labels: ["Cenário Pessimista", "Cenário Base (PE)", "Cenário Otimista"],
        datasets: [
          {
            label: "Superávit Estatutário Reinvestido",
            data: [pessSup, baseSup, optSup],
            backgroundColor: ["#e11d48", "#0b1d3a", "#059669"],
            borderRadius: 6,
            barThickness: 36
          }
        ]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { display: false },
          tooltip: {
            callbacks: {
              label: (ctx) => ` Superávit Reinvestido: ${formatCurrency(ctx.raw)}`
            }
          }
        },
        scales: {
          y: {
            beginAtZero: true,
            ticks: {
              callback: (val) => "R$ " + (val / 1000).toFixed(0) + "k",
              font: { size: 10 }
            },
            grid: { color: "#f1f5f9" }
          },
          x: {
            grid: { display: false },
            ticks: { font: { size: 11, weight: "bold" } }
          }
        }
      }
    });
  }
}

function renderForecastingTable() {
  if (!state.forecasting || !state.forecasting.cenarios || !state.forecasting.labels) return;

  const selectEl = document.getElementById("forecast-table-scenario-select");
  const scenarioKey = selectEl ? selectEl.value : "base";
  const scenarioData = state.forecasting.cenarios[scenarioKey];
  if (!scenarioData) return;

  const tbody = document.getElementById("forecast-table-tbody");
  if (!tbody) return;

  const labels = state.forecasting.labels;
  const d = scenarioData.dados;

  tbody.innerHTML = labels.map((label, idx) => {
    const rec = d.receita[idx] || 0;
    const custo = d.custos[idx] || 0;
    const liq = d.fluxo_liquido[idx] || 0;
    const saldo = d.saldo_acumulado[idx] || 0;

    const liqClass = liq >= 0 ? "text-emerald-700 font-bold" : "text-rose-600 font-bold";

    return `
      <tr class="hover:bg-slate-50 transition-colors">
        <td class="py-2.5 px-3 text-slate-700 font-semibold">${label}</td>
        <td class="py-2.5 px-3 text-right text-slate-800">${formatCurrency(rec)}</td>
        <td class="py-2.5 px-3 text-right text-rose-700">-${formatCurrency(custo)}</td>
        <td class="py-2.5 px-3 text-right ${liqClass}">${formatCurrency(liq)}</td>
        <td class="py-2.5 px-3 text-right text-[#0b1d3a] font-bold">${formatCurrency(saldo)}</td>
        <td class="py-2.5 px-3 text-center">
          <span class="inline-flex items-center gap-1 text-[10px] bg-emerald-50 text-emerald-800 px-2 py-0.5 rounded font-bold border border-emerald-200">
            <i class="fa-solid fa-lock text-[8px]"></i> 100% Retido
          </span>
        </td>
      </tr>
    `;
  }).join("");
}

function exportForecastCSV() {
  if (!state.forecasting || !state.forecasting.labels) {
    alert("Nenhuma projeção disponível para exportação.");
    return;
  }

  const labels = state.forecasting.labels;
  const base = state.forecasting.cenarios.base.dados;
  const opt = state.forecasting.cenarios.otimista.dados;
  const pess = state.forecasting.cenarios.pessimista.dados;

  let csv = "Periodo;Receita_Base;Custos_Base;Fluxo_Base;Saldo_Base;Receita_Otimista;Custos_Otimista;Fluxo_Otimista;Saldo_Otimista;Receita_Pessimista;Custos_Pessimista;Fluxo_Pessimista;Saldo_Pessimista;Destinacao_Legal\n";

  labels.forEach((m, i) => {
    csv += `${m};${base.receita[i]};${base.custos[i]};${base.fluxo_liquido[i]};${base.saldo_acumulado[i]};${opt.receita[i]};${opt.custos[i]};${opt.fluxo_liquido[i]};${opt.saldo_acumulado[i]};${pess.receita[i]};${pess.custos[i]};${pess.fluxo_liquido[i]};${pess.saldo_acumulado[i]};100% Reinvestido (Lei 13.267)\n`;
  });

  const blob = new Blob([csv], { type: "text/csv;charset=utf-8;" });
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.setAttribute("href", url);
  link.setAttribute("download", `nexus_forecasting_${state.forecastHorizon}m_${new Date().toISOString().split("T")[0]}.csv`);
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
}

// ==============================================================================
// MODAL DE AUTENTICAÇÃO / LOGIN RBAC
// ==============================================================================
function openLoginModal() {
  const modal = document.getElementById("modal-login");
  if (modal) modal.classList.remove("hidden");
}

function closeLoginModal() {
  const modal = document.getElementById("modal-login");
  if (modal) modal.classList.add("hidden");
}

function fillLoginPreset(email, password) {
  document.getElementById("login-email").value = email;
  document.getElementById("login-password").value = password;
}

async function submitLogin() {
  const email = document.getElementById("login-email")?.value.trim();
  const password = document.getElementById("login-password")?.value.trim();

  if (!email || !password) {
    alert("Informe o e-mail e senha.");
    return;
  }

  try {
    const res = await fetch("/api/auth/login", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email, password })
    });
    if (!res.ok) throw new Error("Credenciais inválidas");

    const data = await res.json();
    state.user = data.user;
    localStorage.setItem("nexus_user", JSON.stringify(data.user));

    updateUserInterface();
    closeLoginModal();
    alert(`Bem-vindo, ${data.user.nome} (${data.user.cargo || data.user.role})!`);
  } catch (err) {
    alert("Erro na autenticação: " + err.message);
  }
}

// ==============================================================================
// UTILITÁRIOS GERAIS
// ==============================================================================
function formatCurrency(val) {
  if (typeof val !== "number") val = parseFloat(val) || 0.0;
  return val.toLocaleString("pt-BR", { style: "currency", currency: "BRL" });
}

function escapeHtml(str) {
  if (!str) return "";
  return str.replace(/'/g, "\\'").replace(/"/g, "&quot;");
}
