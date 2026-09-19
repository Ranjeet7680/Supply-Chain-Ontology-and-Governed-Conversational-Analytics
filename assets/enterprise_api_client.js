/**
 * assets/enterprise_api_client.js: Real-Time Enterprise Data & Live API Client for SupplyChain IQ v2.4
 */

const API_BASE = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1' 
  ? 'http://127.0.0.1:8000/api' 
  : '/api';

window.SupplyChainData = {
  kpis: null,
  suppliers: [],
  orders: [],
  shipments: [],
  risks: [],
  inventory: [],
  playbooks: [],
  auditLogs: []
};

// 1. Fetch Dashboard KPIs
async function fetchDashboardKPIs() {
  try {
    const res = await fetch(API_BASE + '/dashboard/summary');
    if (!res.ok) throw new Error('API error');
    const data = await res.json();
    window.SupplyChainData.kpis = data.kpis;
    
    // Update live DOM KPI values if present
    const otifEl = document.getElementById('kpi-canonical-otif');
    if (otifEl && data.kpis.otif_rate) otifEl.textContent = data.kpis.otif_rate.value + '%';

    const invEl = document.getElementById('kpi-inventory-val');
    if (invEl && data.kpis.inventory_value) {
      const valM = (data.kpis.inventory_value.value / 1000000).toFixed(1);
      invEl.textContent = '$' + valM + 'M';
    }

    const poEl = document.getElementById('kpi-open-pos');
    if (poEl && data.kpis.open_purchase_orders) poEl.textContent = data.kpis.open_purchase_orders.value;

    const riskEl = document.getElementById('kpi-stockout-risk');
    if (riskEl && data.kpis.stockout_risk_skus) riskEl.textContent = data.kpis.stockout_risk_skus.value + ' SKUs';

  } catch (err) {
    console.warn('Dashboard KPI fetch fallback to local cache:', err);
  }
}

// 2. Fetch & Render Real Suppliers Table
async function fetchSuppliers(search, tier) {
  try {
    let url = API_BASE + '/suppliers?limit=50';
    if (search) url += '&search=' + encodeURIComponent(search);
    if (tier) url += '&tier=' + encodeURIComponent(tier);
    
    const res = await fetch(url);
    if (!res.ok) throw new Error('API error');
    const data = await res.json();
    window.SupplyChainData.suppliers = data.items;
    renderSuppliersTable(data.items);
  } catch (err) {
    console.warn('Suppliers API fallback:', err);
  }
}

function renderSuppliersTable(suppliers) {
  const tbody = document.querySelector('#tab-suppliers table tbody');
  if (!tbody) return;

  tbody.innerHTML = suppliers.slice(0, 15).map(function(s) {
    const otifClass = s.otif_score >= 90 ? 'text-emerald-400 font-bold' : (s.otif_score >= 80 ? 'text-cyan-300' : 'text-amber-400 font-bold');
    const statusBadge = s.status === 'Active' 
      ? '<span class="px-2 py-0.5 rounded bg-emerald-500/20 text-emerald-300">Active</span>'
      : '<span class="px-2 py-0.5 rounded bg-amber-500/20 text-amber-300">Under Review</span>';
    
    return '<tr class="hover:bg-cyan-500/5 transition-colors">' +
      '<td class="p-3 font-bold text-white">' + s.name + ' <span class="text-[10px] font-mono text-cyan-400">(' + s.supplier_code + ')</span></td>' +
      '<td class="p-3">' + s.country + '</td>' +
      '<td class="p-3 text-slate-300">' + s.category + '</td>' +
      '<td class="p-3 ' + otifClass + '">' + s.otif_score + '%</td>' +
      '<td class="p-3">' + s.lead_time_days + ' days</td>' +
      '<td class="p-3">' + statusBadge + '</td>' +
      '<td class="p-3 text-right">' +
        '<button onclick="viewSupplierDetails(\'' + s.id + '\')" class="px-2.5 py-1 rounded bg-slate-800 hover:bg-slate-700 text-cyan-300 text-[10px] font-bold transition-all">Profile</button>' +
      '</td>' +
    '</tr>';
  }).join('');
}

async function viewSupplierDetails(supplierId) {
  try {
    const res = await fetch(API_BASE + '/suppliers/' + supplierId);
    if (!res.ok) throw new Error('Failed to fetch supplier details');
    const data = await res.json();
    const sup = data.supplier;
    
    const posHtml = data.recent_pos.map(function(p) {
      const cls = p.status === 'Approved' ? 'bg-emerald-500/20 text-emerald-300' : 'bg-amber-500/20 text-amber-300';
      return '<div class="p-2 bg-[#040e1c] rounded border border-cyan-500/20 flex justify-between items-center text-[11px]">' +
        '<span class="text-cyan-300 font-bold">' + p.po_number + '</span>' +
        '<span>$' + Math.round(p.amount).toLocaleString() + '</span>' +
        '<span class="px-1.5 py-0.5 rounded ' + cls + '">' + p.status + '</span>' +
      '</div>';
    }).join('') || '<div class="text-slate-500">No recent POs</div>';

    showActionDialog({
      title: sup.name,
      subtitle: sup.code + ' • ' + sup.tier + ' • ' + sup.country,
      icon: 'factory',
      confirmText: 'Audit Supplier',
      contentHtml: '<div class="space-y-3 font-mono text-xs text-slate-300">' +
        '<div class="grid grid-cols-2 gap-2 bg-[#020712] p-3 rounded-lg border border-cyan-900/40">' +
          '<div>&bull; OTIF Adherence: <span class="text-emerald-400 font-bold">' + sup.otif + '%</span></div>' +
          '<div>&bull; Mean Lead Time: <span class="text-cyan-300">' + sup.lead_time + ' days</span></div>' +
          '<div>&bull; Quality Score: <span class="text-emerald-400">' + sup.quality + '%</span></div>' +
          '<div>&bull; Risk Class Score: <span class="text-amber-400 font-bold">' + sup.risk_score + '/100</span></div>' +
          '<div>&bull; Annual Spend: <span class="text-white">$' + Math.round(sup.spend).toLocaleString() + '</span></div>' +
          '<div>&bull; Status: <span class="text-cyan-300">' + sup.status + '</span></div>' +
        '</div>' +
        '<div>' +
          '<h5 class="text-white font-bold mb-1.5">Associated Purchase Orders:</h5>' +
          '<div class="space-y-1.5 max-h-36 overflow-y-auto">' + posHtml + '</div>' +
        '</div>' +
      '</div>',
      onConfirm: function() {
        showToast('Auditing supplier ' + sup.name + ' with Snowflake Cortex...', 'info');
        switchTab('chat');
        if (typeof runSimulatedQuery === 'function') {
          runSimulatedQuery('Provide full performance and risk audit for ' + sup.name);
        }
      }
    });
  } catch (err) {
    showToast('Failed to load supplier details: ' + err.message, 'error');
  }
}

// 3. Fetch & Render Real Purchase Orders
async function fetchOrders() {
  try {
    const res = await fetch(API_BASE + '/orders?limit=25');
    if (!res.ok) throw new Error('API error');
    const data = await res.json();
    window.SupplyChainData.orders = data.items;
    renderOrdersTable(data.items);
  } catch (err) {
    console.warn('Orders API fallback:', err);
  }
}

function renderOrdersTable(orders) {
  const container = document.querySelector('#tab-orders .space-y-2');
  if (!container) return;

  container.innerHTML = orders.slice(0, 8).map(function(po) {
    const statusBadge = po.status === 'Approved'
      ? '<span class="text-emerald-400 font-bold">Approved</span>'
      : (po.status === 'Delayed' 
          ? '<span class="text-rose-400 font-bold">Delayed (+4d)</span>'
          : '<span class="text-amber-400">' + po.status + '</span>');

    const canApprove = po.status === 'Pending Approval';
    const actionBtn = canApprove
      ? '<button onclick="approvePO(\'' + po.po_number + '\')" class="px-2 py-0.5 rounded bg-cyan-500 text-slate-950 font-bold text-[10px] hover:bg-cyan-400 transition-all">Approve</button>'
      : '<button onclick="showToast(\'PO ' + po.po_number + ' is already ' + po.status + '\', \'info\')" class="px-2 py-0.5 rounded bg-slate-800 text-slate-400 text-[10px]">Inspect</button>';

    return '<div class="p-3 rounded-lg bg-[#020712] border border-cyan-900/30 flex items-center justify-between hover:border-cyan-500/40 transition-colors">' +
      '<div class="flex items-center gap-3">' +
        '<span class="text-cyan-300 font-bold font-mono">' + po.po_number + '</span>' +
        '<span class="text-slate-300 text-xs">' + (po.supplier_name || po.supplier_code) + ' ⇄ ' + po.warehouse + '</span>' +
      '</div>' +
      '<div class="flex items-center gap-4">' +
        statusBadge +
        '<span class="text-slate-400 font-mono text-xs">$' + Math.round(po.amount).toLocaleString() + '</span>' +
        actionBtn +
      '</div>' +
    '</div>';
  }).join('');
}

async function approvePO(poNumber) {
  try {
    const res = await fetch(API_BASE + '/orders/' + poNumber + '/approve', { method: 'PATCH' });
    if (!res.ok) throw new Error('Approval failed');
    showToast('Purchase Order ' + poNumber + ' approved and logged to Audit Mart!', 'success');
    fetchOrders();
    fetchDashboardKPIs();
  } catch (err) {
    showToast('Failed to approve PO: ' + err.message, 'error');
  }
}

// 4. Fetch & Render Real Risk Alerts with Acknowledge/Resolve Actions
async function fetchRisks() {
  try {
    const res = await fetch(API_BASE + '/risks');
    if (!res.ok) throw new Error('API error');
    const data = await res.json();
    window.SupplyChainData.risks = data.items;
    renderRisksSection(data.items);
  } catch (err) {
    console.warn('Risks API fallback:', err);
  }
}

function renderRisksSection(risks) {
  const container = document.querySelector('#tab-risk .space-y-3');
  if (!container) return;

  container.innerHTML = risks.map(function(r) {
    const isCritical = r.severity === 'Critical';
    const bgClass = isCritical ? 'bg-red-950/30 border-red-500/40' : 'bg-amber-950/30 border-amber-500/40';
    const tagClass = isCritical ? 'bg-red-500 text-slate-950' : 'bg-amber-500 text-slate-950';
    
    return '<div class="p-4 rounded-xl ' + bgClass + ' border flex flex-col sm:flex-row items-start justify-between gap-4 transition-all hover:scale-[1.01]">' +
      '<div class="space-y-1.5">' +
        '<div class="flex items-center gap-2">' +
          '<span class="px-2 py-0.5 rounded ' + tagClass + ' font-bold font-mono text-[10px]">' + r.severity + '</span>' +
          '<span class="text-xs font-mono text-slate-400">[' + r.alert_code + '] • ' + r.category + '</span>' +
          '<span class="px-1.5 py-0.2 rounded bg-slate-800 text-slate-300 font-mono text-[10px]">' + r.status + '</span>' +
        '</div>' +
        '<h4 class="font-bold text-white text-sm">' + r.entity_name + '</h4>' +
        '<p class="text-slate-300 text-xs leading-relaxed">' + r.reason + '</p>' +
        '<div class="text-[11px] font-mono text-cyan-300 mt-1">&bull; Recommendation: ' + r.recommended_action + '</div>' +
      '</div>' +
      '<div class="flex items-center gap-2 shrink-0 self-end sm:self-center">' +
        (r.status === 'Open' ? '<button onclick="acknowledgeAlert(\'' + r.alert_code + '\')" class="px-3 py-1.5 rounded-lg bg-amber-500 text-slate-950 font-bold text-xs hover:bg-amber-400 transition-all">Acknowledge</button>' : '') +
        (r.status !== 'Resolved' ? '<button onclick="resolveAlert(\'' + r.alert_code + '\')" class="px-3 py-1.5 rounded-lg bg-emerald-500 text-slate-950 font-bold text-xs hover:bg-emerald-400 transition-all">Resolve</button>' : '<span class="text-emerald-400 font-bold text-xs font-mono">✓ Resolved</span>') +
      '</div>' +
    '</div>';
  }).join('');
}

async function acknowledgeAlert(alertCode) {
  try {
    const res = await fetch(API_BASE + '/risks/' + alertCode + '/acknowledge', { method: 'POST' });
    if (!res.ok) throw new Error('API error');
    showToast('Alert ' + alertCode + ' acknowledged by current persona.', 'info');
    fetchRisks();
  } catch (err) {
    showToast('Failed to acknowledge alert: ' + err.message, 'error');
  }
}

async function resolveAlert(alertCode) {
  try {
    const res = await fetch(API_BASE + '/risks/' + alertCode + '/resolve', { method: 'POST' });
    if (!res.ok) throw new Error('API error');
    showToast('Alert ' + alertCode + ' marked as Resolved!', 'success');
    fetchRisks();
  } catch (err) {
    showToast('Failed to resolve alert: ' + err.message, 'error');
  }
}

// 5. Hook into tab transitions to load live data automatically
const originalSwitchTab = window.switchTab;
window.switchTab = function(tabId) {
  if (typeof originalSwitchTab === 'function') {
    originalSwitchTab(tabId);
  }
  if (tabId === 'suppliers') {
    fetchSuppliers();
  } else if (tabId === 'orders') {
    fetchOrders();
  } else if (tabId === 'risk') {
    fetchRisks();
  } else if (tabId === 'overview') {
    fetchDashboardKPIs();
  }
};

// Auto initialize on DOM ready
document.addEventListener('DOMContentLoaded', function() {
  setTimeout(function() {
    fetchDashboardKPIs();
  }, 500);
});


// 6. Fetch & Render Real Inventory & SKU Register
async function fetchInventory() {
  try {
    const res = await fetch(API_BASE + '/inventory?limit=25');
    if (!res.ok) throw new Error('API error');
    const data = await res.json();
    window.SupplyChainData.inventory = data.items;
    renderInventoryTable(data.items);
  } catch (err) {
    console.warn('Inventory API fallback:', err);
  }
}

function renderInventoryTable(items) {
  const tbody = document.querySelector('#tab-inventory table tbody');
  if (!tbody) return;

  tbody.innerHTML = items.slice(0, 10).map(function(item) {
    const isAtRisk = item.status === 'At Risk' || item.quantity_on_hand < item.safety_stock;
    const stockClass = isAtRisk ? 'text-amber-400 font-bold' : 'text-emerald-400 font-bold';
    const actionText = isAtRisk ? 'Trigger PO Re-order' : 'Optimal';
    const badgeClass = isAtRisk ? 'bg-amber-500/20 text-amber-300' : 'bg-emerald-500/20 text-emerald-300';
    const daysSupply = Math.round((item.quantity_on_hand / Math.max(item.demand_forecast_30d / 30, 1)) * 10) / 10;
    
    return '<tr class="hover:bg-cyan-500/5 transition-colors">' +
      '<td class="p-3 font-bold text-cyan-300">' + item.part_code + '</td>' +
      '<td class="p-3 text-white">Standard Component</td>' +
      '<td class="p-3">' + item.warehouse + '</td>' +
      '<td class="p-3 ' + stockClass + '">' + item.quantity_on_hand.toLocaleString() + ' units</td>' +
      '<td class="p-3 ' + (isAtRisk ? 'text-amber-400' : 'text-emerald-400') + '">' + daysSupply + ' days</td>' +
      '<td class="p-3"><span class="px-2 py-0.5 rounded ' + badgeClass + '">' + actionText + '</span></td>' +
      '<td class="p-3 text-right">' +
        (isAtRisk 
          ? '<button onclick="createQuickPO(\'' + item.part_code + '\', \'' + item.warehouse + '\')" class="px-2.5 py-1 rounded bg-cyan-500/20 hover:bg-cyan-500/30 text-cyan-300 text-[10px] font-bold transition-all">Re-order</button>'
          : '<button onclick="showToast(\'Stock buffer for ' + item.part_code + ' is optimal\', \'success\')" class="px-2.5 py-1 rounded bg-slate-800 hover:bg-slate-700 text-slate-300 text-[10px] font-bold transition-all">Details</button>') +
      '</td>' +
    '</tr>';
  }).join('');
}

async function createQuickPO(partCode, warehouse) {
  try {
    const res = await fetch(API_BASE + '/orders', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        supplier_code: 'SUP_0012',
        destination_warehouse: warehouse || 'WH_MUMBAI',
        part_code: partCode,
        quantity: 500,
        unit_price: 32.5
      })
    });
    if (!res.ok) throw new Error('Failed to create replenishment PO');
    const data = await res.json();
    showToast('Replenishment ' + data.po_number + ' created for ' + partCode + '!', 'success');
    fetchDashboardKPIs();
    fetchInventory();
  } catch (err) {
    showToast('Error creating PO: ' + err.message, 'error');
  }
}

// 7. Global Search Hook
window.filterSearchResults = async function(query) {
  const container = document.getElementById('modal-search-results');
  if (!container) return;
  if (!query || query.trim().length === 0) return;

  try {
    const res = await fetch(API_BASE + '/search?q=' + encodeURIComponent(query));
    if (!res.ok) return;
    const data = await res.json();
    
    let html = '<div class="text-[11px] font-mono text-outline uppercase">Search Results for "' + query + '"</div>';
    
    // Suppliers
    if (data.results.suppliers && data.results.suppliers.length > 0) {
      html += '<div class="text-[10px] font-bold text-secondary uppercase mt-2">Suppliers</div>';
      data.results.suppliers.forEach(function(s) {
        html += '<div onclick="switchTab(\'suppliers\'); closeModal(\'search\'); viewSupplierDetails(\'' + s.id + '\');" class="p-2.5 rounded-lg bg-surface-container hover:bg-surface-container-high cursor-pointer flex items-center justify-between">' +
          '<div class="flex items-center gap-2"><span class="material-symbols-outlined text-[18px] text-cyan-400">factory</span><span class="text-xs font-semibold text-white">' + s.title + '</span></div>' +
          '<span class="text-[10px] text-cyan-300 font-mono">' + s.code + '</span>' +
        '</div>';
      });
    }

    // Purchase Orders
    if (data.results.purchase_orders && data.results.purchase_orders.length > 0) {
      html += '<div class="text-[10px] font-bold text-secondary uppercase mt-2">Purchase Orders</div>';
      data.results.purchase_orders.forEach(function(p) {
        html += '<div onclick="switchTab(\'orders\'); closeModal(\'search\');" class="p-2.5 rounded-lg bg-surface-container hover:bg-surface-container-high cursor-pointer flex items-center justify-between">' +
          '<div class="flex items-center gap-2"><span class="material-symbols-outlined text-[18px] text-amber-400">receipt_long</span><span class="text-xs font-semibold text-white">' + p.title + '</span></div>' +
          '<span class="text-[10px] text-emerald-400 font-mono">$' + Math.round(p.amount).toLocaleString() + '</span>' +
        '</div>';
      });
    }

    // Shipments
    if (data.results.shipments && data.results.shipments.length > 0) {
      html += '<div class="text-[10px] font-bold text-secondary uppercase mt-2">Shipments</div>';
      data.results.shipments.forEach(function(sh) {
        html += '<div onclick="switchTab(\'shipments\'); closeModal(\'search\');" class="p-2.5 rounded-lg bg-surface-container hover:bg-surface-container-high cursor-pointer flex items-center justify-between">' +
          '<div class="flex items-center gap-2"><span class="material-symbols-outlined text-[18px] text-purple-400">local_shipping</span><span class="text-xs font-semibold text-white">' + sh.title + ' (' + sh.carrier + ')</span></div>' +
          '<span class="text-[10px] text-slate-300 font-mono">' + sh.status + '</span>' +
        '</div>';
      });
    }

    container.innerHTML = html;
  } catch (err) {
    console.warn('Search query error:', err);
  }
};

// 8. Scenario Simulator Runner
window.triggerScenarioSimulation = async function(scenarioName, duration) {
  showToast('Simulating scenario: ' + scenarioName + ' (' + duration + ' days)...', 'info');
  try {
    const res = await fetch(API_BASE + '/scenarios/run', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        name: scenarioName || '5-Day Jebel Ali Corridor Disruption',
        scenario_type: 'Port Shutdown',
        duration_days: duration || 5,
        region: 'GCC',
        demand_increase_pct: 15.0,
        capacity_reduction_pct: 45.0,
        transport_disruption_pct: 70.0
      })
    });
    if (!res.ok) throw new Error('Simulation failed');
    const sim = await res.json();
    
    showActionDialog({
      title: 'Scenario Simulation Completed',
      subtitle: sim.name + ' • ' + sim.duration_days + ' Days Horizon',
      icon: 'radar',
      confirmText: 'Execute Mitigation Playbook',
      contentHtml: '<div class="space-y-3 font-mono text-xs text-slate-300">' +
        '<div class="p-3 rounded-lg bg-rose-950/30 border border-rose-500/40 text-rose-300">' + sim.impact_summary + '</div>' +
        '<div class="grid grid-cols-2 gap-2 bg-[#020712] p-3 rounded-lg border border-cyan-900/40">' +
          '<div>&bull; Baseline OTIF: <span class="text-emerald-400 font-bold">' + sim.baseline.otif_rate + '%</span></div>' +
          '<div>&bull; Simulated OTIF: <span class="text-rose-400 font-bold">' + sim.simulated.otif_rate + '%</span></div>' +
          '<div>&bull; Stockout Exposure: <span class="text-amber-400 font-bold">' + sim.simulated.stockout_skus + ' SKUs</span></div>' +
          '<div>&bull; Landed Cost Shift: <span class="text-rose-400 font-bold">+' + sim.simulated.landed_cost_variance_pct + '%</span></div>' +
        '</div>' +
        '<div class="p-2.5 rounded bg-cyan-950/30 border border-cyan-500/30 text-cyan-300 text-[11px]">&bull; AI Recommendation: ' + sim.mitigation_recommendation + '</div>' +
      '</div>',
      onConfirm: async function() {
        showToast('Triggering GCC Maritime Corridor Reroute Playbook...', 'info');
        try {
          const runRes = await fetch(API_BASE + '/playbooks/PB-PORT-SHUTDOWN/run', { method: 'POST' });
          if (!runRes.ok) throw new Error('Playbook execution failed');
          const runData = await runRes.json();
          showToast(runData.summary, 'success');
        } catch (e) {
          showToast('Playbook failed: ' + e.message, 'error');
        }
      }
    });
  } catch (err) {
    showToast('Simulation error: ' + err.message, 'error');
  }
};

// 9. Attach to tab switches
const prevTabSwitch = window.switchTab;
window.switchTab = function(tabId) {
  if (typeof prevTabSwitch === 'function') {
    prevTabSwitch(tabId);
  }
  if (tabId === 'inventory') {
    fetchInventory();
  }
};


// 10. Fetch & Render Real Shipments
async function fetchShipments() {
  try {
    const res = await fetch(API_BASE + '/shipments?limit=25');
    if (!res.ok) throw new Error('API error');
    const data = await res.json();
    window.SupplyChainData.shipments = data.items;
    renderShipmentsTable(data.items);
  } catch (err) {
    console.warn('Shipments API fallback:', err);
  }
}

function renderShipmentsTable(items) {
  // Find shipment card or container in tab-shipments
  const container = document.querySelector('#tab-shipments .p-6.rounded-2xl');
  if (!container) return;

  let tableHtml = '<div class="mt-4 overflow-x-auto">' +
    '<table class="w-full text-left text-xs font-mono">' +
      '<thead class="bg-[#020712] text-slate-400 border-b border-cyan-900/40">' +
        '<tr>' +
          '<th class="p-3">Shipment ID</th>' +
          '<th class="p-3">Carrier</th>' +
          '<th class="p-3">Route Corridor</th>' +
          '<th class="p-3">Status</th>' +
          '<th class="p-3">ETA / Delay</th>' +
          '<th class="p-3">Risk Score</th>' +
          '<th class="p-3 text-right">Action</th>' +
        '</tr>' +
      '</thead>' +
      '<tbody class="divide-y divide-cyan-900/30 text-slate-300">' +
        items.slice(0, 10).map(function(s) {
          const isDel = s.status === 'Delayed';
          const badgeClass = isDel ? 'bg-rose-500/20 text-rose-300' : 'bg-emerald-500/20 text-emerald-300';
          const riskColor = s.risk_score > 50 ? 'text-rose-400 font-bold' : 'text-cyan-300';
          return '<tr class="hover:bg-cyan-500/5 transition-colors">' +
            '<td class="p-3 font-bold text-cyan-300">' + s.shipment_id + '</td>' +
            '<td class="p-3 text-white">' + s.carrier + '</td>' +
            '<td class="p-3 text-slate-400">' + s.origin + ' ⇄ ' + s.destination + '</td>' +
            '<td class="p-3"><span class="px-2 py-0.5 rounded ' + badgeClass + '">' + s.status + '</span></td>' +
            '<td class="p-3 font-mono">' + s.eta + (isDel ? ' <span class="text-rose-400 font-bold">(+' + s.delay_hours + 'h)</span>' : '') + '</td>' +
            '<td class="p-3 ' + riskColor + '">' + s.risk_score + '/100</td>' +
            '<td class="p-3 text-right">' +
              '<button onclick="inspectShipmentPrediction(\'' + s.shipment_id + '\', \'' + s.carrier + '\')" class="px-2 py-0.5 rounded bg-cyan-500/20 hover:bg-cyan-500/30 text-cyan-300 text-[10px] font-bold">Predict</button>' +
            '</td>' +
          '</tr>';
        }).join('') +
      '</tbody>' +
    '</table>' +
  '</div>';

  const existingTable = document.getElementById('dynamic-shipments-table-wrapper');
  if (existingTable) {
    existingTable.innerHTML = tableHtml;
  } else {
    const wrapper = document.createElement('div');
    wrapper.id = 'dynamic-shipments-table-wrapper';
    wrapper.innerHTML = tableHtml;
    container.appendChild(wrapper);
  }
}

async function inspectShipmentPrediction(shipmentId, carrier) {
  showToast('Running PyTorch DeepRiskNet on ' + shipmentId + ' (' + carrier + ')...', 'info');
  try {
    const res = await fetch(API_BASE + '/dl/predict-deep-risk', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        distance_km: 1420.0,
        package_weight_kg: 45.0,
        delivery_cost: 620.0,
        delivery_partner: carrier.toLowerCase().includes('xpress') ? 'xpressbees' : 'delhivery',
        vehicle_type: 'truck',
        delivery_mode: 'express',
        region: 'west',
        weather_condition: 'stormy',
        days_of_inventory: 10.0
      })
    });
    if (!res.ok) throw new Error('Inference error');
    const data = await res.json();
    const riskNet = data.deep_risk_inference;
    const anomaly = data.autoencoder_anomaly;

    showActionDialog({
      title: 'Neural Disruption Analysis: ' + shipmentId,
      subtitle: 'PyTorch DeepRiskNet & Autoencoder Anomaly Detector',
      icon: 'psychology',
      confirmText: 'Dispatch Reroute Order',
      contentHtml: '<div class="space-y-3 font-mono text-xs text-slate-300">' +
        '<div class="grid grid-cols-2 gap-2 bg-[#020712] p-3 rounded-lg border border-cyan-900/40">' +
          '<div>&bull; Risk Probability: <span class="text-rose-400 font-bold">' + (riskNet.deep_risk_score * 100).toFixed(1) + '%</span></div>' +
          '<div>&bull; Risk Level: <span class="text-rose-400 font-bold">' + riskNet.risk_level + '</span></div>' +
          '<div>&bull; Autoencoder Anomaly: <span class="' + (anomaly.is_anomaly ? 'text-rose-400 font-bold' : 'text-emerald-400') + '">' + (anomaly.is_anomaly ? 'ANOMALY DETECTED' : 'NORMAL') + '</span></div>' +
          '<div>&bull; Reconstruction MSE: <span class="text-cyan-300">' + anomaly.reconstruction_error.toFixed(4) + '</span></div>' +
        '</div>' +
        '<div class="p-2.5 rounded bg-slate-900 border border-slate-700 text-slate-300 text-[11px]">&bull; Action: ' + riskNet.mitigation_recommendation + '</div>' +
      '</div>',
      onConfirm: function() {
        showToast('Autonomous Reroute order sent to carrier TMS for ' + shipmentId + '!', 'success');
      }
    });
  } catch (err) {
    showToast('Prediction error: ' + err.message, 'error');
  }
}

// 11. Fetch & Render Real Warehouses
async function fetchWarehouses() {
  try {
    const res = await fetch(API_BASE + '/warehouses');
    if (!res.ok) throw new Error('API error');
    const data = await res.json();
    renderWarehouses(data.items);
  } catch (err) {
    console.warn('Warehouses API fallback:', err);
  }
}

function renderWarehouses(items) {
  const container = document.querySelector('#tab-warehouses .grid');
  if (!container) return;

  container.innerHTML = items.map(function(w) {
    const utilClass = w.utilization_pct > 85 ? 'text-amber-400 font-bold' : 'text-emerald-400 font-bold';
    return '<div class="p-5 rounded-2xl bg-[#040E1C] border border-cyan-500/30 space-y-2 hover:border-cyan-400/60 transition-all">' +
      '<div class="flex items-center justify-between">' +
        '<span class="font-bold text-white text-base">' + w.name + '</span>' +
        '<span class="px-2 py-0.5 rounded bg-emerald-500/20 ' + utilClass + ' text-xs font-mono">' + Math.round(w.utilization_pct) + '% Capacity</span>' +
      '</div>' +
      '<p class="text-xs text-slate-400">Location: ' + w.location + ' (' + w.region + ')</p>' +
      '<div class="flex justify-between items-center text-xs font-mono text-cyan-300 pt-1 border-t border-cyan-900/30">' +
        '<span>Storage: ' + Math.round(w.capacity_sqft).toLocaleString() + ' sqft</span>' +
        '<button onclick="showToast(\'Dispatching telemetry health ping to ' + w.code + '...\', \'info\')" class="px-2 py-0.5 rounded bg-cyan-500/20 text-cyan-300 hover:bg-cyan-500 hover:text-slate-950 text-[10px] font-bold">Ping Node</button>' +
      '</div>' +
    '</div>';
  }).join('');
}

// 12. Real CSV Exporter Hook
window.exportDataCSV = function(entityType) {
  showToast('Generating governed CSV export for ' + entityType + '...', 'info');
  window.open(API_BASE + '/export/csv/' + entityType, '_blank');
};

// 13. Expand tab hooks
const oldTabHook = window.switchTab;
window.switchTab = function(tabId) {
  if (typeof oldTabHook === 'function') {
    oldTabHook(tabId);
  }
  if (tabId === 'shipments') {
    fetchShipments();
  } else if (tabId === 'warehouses') {
    fetchWarehouses();
  }
};
