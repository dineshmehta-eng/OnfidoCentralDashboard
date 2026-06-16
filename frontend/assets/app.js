// Onfido Dashboard Frontend — FastAPI Edition
const BASE_API = ""; // same origin
const API_KEY = "";  // fill if backend API_KEY is enabled

function buildHeaders() {
  const h = { "Content-Type": "application/json" };
  if (API_KEY) h["X-API-Key"] = API_KEY;
  return h;
}

async function apiPost(url, payload) {
  const res = await fetch(`${BASE_API}${url}`, {
    method: "POST",
    headers: buildHeaders(),
    body: JSON.stringify(payload || {})
  });
  if (!res.ok) throw new Error("API error: " + res.status);
  return await res.json();
}

async function apiGet(url) {
  const h = {};
  if (API_KEY) h["X-API-Key"] = API_KEY;
  const res = await fetch(`${BASE_API}${url}`, { headers: h });
  if (!res.ok) throw new Error("API error: " + res.status);
  return await res.json();
}

function showLoader(show) {
  const el = document.getElementById("loader");
  if (el) el.classList.toggle("active", show);
  if (show) clearErrors();
}

function clearErrors() {
  const el = document.getElementById("alertsContainer");
  if (el) el.innerHTML = "";
}

function showError(message, type = "danger") {
  const container = document.getElementById("alertsContainer");
  if (!container) return;
  const div = document.createElement("div");
  div.className = `alert alert-${type}`;
  div.textContent = message;
  container.appendChild(div);
}

function setText(id, text) {
  const el = document.getElementById(id);
  if (el) el.textContent = text;
}

let currentTab = "overview";
let chartInstances = {};

function switchTab(tabId) {
  currentTab = tabId;
  document.querySelectorAll(".tab").forEach(t => t.classList.toggle("active", t.dataset.target === tabId));
  document.querySelectorAll(".tab-content").forEach(c => c.classList.toggle("active", c.id === tabId));
}

const HEADER_LABELS = {
  "Analyst_Email": "Analyst",
  "TL_Name": "TL",
  "AM": "AM",
  "QA_Name": "QA",
  "Category": "Category",
  "Location": "Location",
  "AON_Wise": "AON",
  "Month": "Month",
  "Date": "Date",
  "Slot": "Slot",
  "Status": "Status",
  "Reason": "Reason",
  "Total_Task": "Tasks",
  "Total_AHT": "Total AHT",
  "avgAht": "Avg AHT",
  "POA_Task": "POA Tasks",
  "POA_AHT": "POA AHT",
  "Mis_Fraud": "Mis Fraud",
  "Total_Fraud": "Total Fraud",
  "WRN_Fraud": "WRN Fraud",
  "Total_Clear": "Total Clear",
  "Ext_Mis_Fraud": "Ext Mis Fraud",
  "Ext_Total_Fraud": "Ext Total Fraud",
  "Ext_WRN_Fraud": "Ext WRN Fraud",
  "Ext_Total_Clear": "Ext Total Clear",
  "Ext_Manual_FARError": "Ext Manual FAR Error",
  "Ext_Manual_FAR": "Ext Manual FAR",
  "Ext_Manual_FRRError": "Ext Manual FRR Error",
  "Ext_Manual_FRR": "Ext Manual FRR",
  "Int_Ext_Error": "Int Ext Error",
  "Int_Ext_Audits": "Int Ext Audits",
  "Int_Raw_ExtError": "Int Raw Ext Error",
  "Int_Raw_Ext_Audits": "Int Raw Ext Audits",
  "Tasks": "Tasks",
  "Utilization": "Utilization",
  "Live_POA": "Live POA",
  "ETM": "ETM",
  "Skipped": "Skipped",
  "Tenure_Months": "Tenure (Months)",
  "Attrition_Risk": "Attrition Risk",
  "totalTasks": "Total Tasks",
  "poaTasks": "POA Tasks",
  "poaAvgAht": "POA Avg AHT",
  "intFar": "Int FAR %",
  "intFrr": "Int FRR %",
  "extFar": "Ext FAR %",
  "extFrr": "Ext FRR %",
  "extManualFar": "Ext Manual FAR %",
  "extManualFrr": "Ext Manual FRR %",
  "intExt": "Int Ext %",
  "intRaw": "Int Raw %",
  "overallError": "Overall Error %"
};

function getHeaderLabel(key) {
  return HEADER_LABELS[key] || key;
}

// Table sorting state
const tableOriginalData = {};
const tableSortState = {};

function sortTable(tableId, key) {
  const rows = tableOriginalData[tableId];
  if (!rows || !rows.length) return;

  const current = tableSortState[tableId];
  let direction = "asc";
  if (current && current.key === key) {
    direction = current.direction === "asc" ? "desc" : "asc";
  }
  tableSortState[tableId] = { key, direction };

  const sorted = [...rows].sort((a, b) => {
    const av = a[key];
    const bv = b[key];
    if (av == null) return 1;
    if (bv == null) return -1;
    if (typeof av === "number" && typeof bv === "number") {
      return direction === "asc" ? av - bv : bv - av;
    }
    return direction === "asc"
      ? String(av).localeCompare(String(bv))
      : String(bv).localeCompare(String(av));
  });

  renderTable(tableId, sorted);
}

function getSortIndicator(tableId, key) {
  const s = tableSortState[tableId];
  if (!s || s.key !== key) return "";
  return s.direction === "asc" ? " ▲" : " ▼";
}

function getFilters() {
  return {
    month: document.getElementById("filterMonth")?.value || "",
    analyst: document.getElementById("filterAnalyst")?.value || "",
    tl: document.getElementById("filterTL")?.value || "",
    am: document.getElementById("filterAM")?.value || "",
    qa: document.getElementById("filterQA")?.value || "",
    category: document.getElementById("filterCategory")?.value || "",
    location: document.getElementById("filterLocation")?.value || "",
  };
}

function collectActiveTabData() {
  const tabContent = document.querySelector(".tab-content.active");
  if (!tabContent) return [];
  const tables = tabContent.querySelectorAll("table");
  let data = [];
  tables.forEach(tbl => {
    const rows = tableOriginalData[tbl.id];
    if (rows && rows.length) {
      rows.forEach(r => {
        const row = { ...r, _Source: tbl.id };
        data.push(row);
      });
    }
  });
  return data;
}

async function exportCurrentTab() {
  const tab = currentTab;
  const data = collectActiveTabData();
  if (!data.length) {
    showError("No data to export for this tab.", "warning");
    return;
  }
  try {
    const payload = { tab, data, filters: getFilters() };
    const res = await fetch(`${BASE_API}/api/export`, {
      method: "POST",
      headers: buildHeaders(),
      body: JSON.stringify(payload)
    });
    if (!res.ok) throw new Error("Export failed: " + res.status);
    const blob = await res.blob();
    const dateStr = new Date().toISOString().slice(0, 10).replace(/-/g, "");
    const filename = `Onfido_${tab}_${dateStr}.xlsx`;
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    a.remove();
    window.URL.revokeObjectURL(url);
  } catch (e) {
    showError("Export error: " + e.message);
  }
}

function destroyChart(id) {
  if (chartInstances[id]) {
    chartInstances[id].destroy();
    delete chartInstances[id];
  }
}

function renderBarChart(canvasId, labels, data, label, stacked = false) {
  const ctx = document.getElementById(canvasId);
  if (!ctx) return;
  if (typeof Chart === "undefined") return;
  destroyChart(canvasId);
  chartInstances[canvasId] = new Chart(ctx.getContext("2d"), {
    type: "bar",
    data: {
      labels,
      datasets: [{
        label,
        data,
        backgroundColor: "rgba(59,130,246,0.6)",
        borderColor: "#3b82f6",
        borderWidth: 1
      }]
    },
    options: {
      responsive: true,
      plugins: { legend: { display: true } },
      scales: {
        x: { stacked },
        y: { stacked, beginAtZero: true }
      }
    }
  });
}

function renderPieChart(canvasId, labels, data, label) {
  const ctx = document.getElementById(canvasId);
  if (!ctx) return;
  if (typeof Chart === "undefined") return;
  destroyChart(canvasId);
  const palette = ["#3b82f6", "#10b981", "#f59e0b", "#ef4444", "#8b5cf6", "#ec4899"];
  chartInstances[canvasId] = new Chart(ctx.getContext("2d"), {
    type: "pie",
    data: {
      labels,
      datasets: [{
        label,
        data,
        backgroundColor: palette,
        borderColor: "#ffffff",
        borderWidth: 1
      }]
    },
    options: { responsive: true, plugins: { legend: { display: true } } }
  });
}

function renderDoughnutChart(canvasId, labels, data, label) {
  const ctx = document.getElementById(canvasId);
  if (!ctx) return;
  if (typeof Chart === "undefined") return;
  destroyChart(canvasId);
  const palette = ["#ef4444", "#f59e0b", "#10b981", "#3b82f6", "#8b5cf6"];
  chartInstances[canvasId] = new Chart(ctx.getContext("2d"), {
    type: "doughnut",
    data: {
      labels,
      datasets: [{
        label,
        data,
        backgroundColor: palette,
        borderColor: "#ffffff",
        borderWidth: 1
      }]
    },
    options: { responsive: true, plugins: { legend: { display: true } } }
  });
}

function inferLabelAndValueKeys(rows) {
  if (!rows || !rows.length) return [null, null];
  const keys = Object.keys(rows[0]);
  const knownLabels = ["Analyst_Email", "TL_Name", "AM", "QA_Name", "Category", "Location", "AON_Wise", "Month", "Date", "Slot", "Status", "Reason"];
  let labelKey = null;
  for (const k of knownLabels) {
    if (keys.includes(k)) { labelKey = k; break; }
  }
  let valueKey = null;
  for (const k of keys) {
    if (k === labelKey) continue;
    const v = rows[0][k];
    if (v != null && !isNaN(parseFloat(String(v).replace(/,/g, "").replace("%", "")))) {
      valueKey = k; break;
    }
  }
  if (!labelKey) labelKey = keys[0];
  if (!valueKey) valueKey = keys[1] || keys[0];
  return [labelKey, valueKey];
}

function renderSimpleBarChart(canvasId, rows) {
  const ctx = document.getElementById(canvasId);
  if (!ctx) return;
  if (typeof Chart === "undefined") return;
  if (!rows || !rows.length) { destroyChart(canvasId); return; }
  const [labelKey, valueKey] = inferLabelAndValueKeys(rows);
  if (!labelKey || !valueKey) return;
  const labels = rows.map(r => r[labelKey] || "");
  const data = rows.map(r => parseFloat(String(r[valueKey]).replace(/,/g, "").replace("%", "")) || 0);
  destroyChart(canvasId);
  chartInstances[canvasId] = new Chart(ctx.getContext("2d"), {
    type: "bar",
    data: {
      labels,
      datasets: [{
        label: getHeaderLabel(valueKey),
        data,
        backgroundColor: "rgba(16,185,129,0.6)",
        borderColor: "#10b981",
        borderWidth: 1
      }]
    },
    options: { responsive: true, plugins: { legend: { display: true } }, scales: { y: { beginAtZero: true } } }
  });
}

function parseNumericValue(raw) {
  if (raw == null) return NaN;
  const s = String(raw).replace(/,/g, "").replace("%", "").trim();
  const n = parseFloat(s);
  return isNaN(n) ? NaN : n;
}

function getCellStyle(key, rawValue) {
  const val = parseNumericValue(rawValue);
  if (isNaN(val)) return "";
  const k = String(key).toLowerCase();
  let bg = "", color = "";
  const apply = (c, b) => { color = c; bg = b; };
  if (k.includes("far") || k.includes("frr") || k.includes("error")) {
    if (val > 5) apply("#7f1d1d", "#fca5a5");
    else if (val < 2) apply("#064e3b", "#6ee7b7");
    else apply("#92400e", "#fcd34d");
  } else if (k.includes("aht")) {
    if (val > 600) apply("#7f1d1d", "#fca5a5");
    else if (val < 300) apply("#064e3b", "#6ee7b7");
    else apply("#92400e", "#fcd34d");
  } else if (k.includes("fraud")) {
    if (val > 3) apply("#7f1d1d", "#fca5a5");
    else if (val < 1) apply("#064e3b", "#6ee7b7");
    else apply("#92400e", "#fcd34d");
  } else if (k.includes("clear") || k.includes("accuracy")) {
    if (val > 98) apply("#064e3b", "#6ee7b7");
    else if (val >= 95) apply("#92400e", "#fcd34d");
    else apply("#7f1d1d", "#fca5a5");
  } else if (k.includes("util")) {
    if (val > 85) apply("#064e3b", "#6ee7b7");
    else if (val >= 75) apply("#92400e", "#fcd34d");
    else apply("#7f1d1d", "#fca5a5");
  } else if (k.includes("skip")) {
    if (val > 5) apply("#7f1d1d", "#fca5a5");
  } else if (k.includes("sla")) {
    if (val < 2) apply("#064e3b", "#6ee7b7");
    else if (val <= 4) apply("#92400e", "#fcd34d");
    else apply("#7f1d1d", "#fca5a5");
  } else {
    if (val > 1000) apply("#7f1d1d", "#fca5a5");
  }
  if (bg) return `background-color:${bg};color:${color};`;
  return "";
}

async function loadInit() {
  try {
    const data = await apiGet("/api/init");
    if (!data.success) return;
    populateSelect("filterMonth", data.filters?.months || []);
    populateSelect("filterAnalyst", data.filters?.analysts || []);
    populateSelect("filterTL", data.filters?.tls || []);
    populateSelect("filterAM", data.filters?.ams || []);
    populateSelect("filterQA", data.filters?.qas || []);
    populateSelect("filterCategory", data.filters?.categories || []);
    populateSelect("filterLocation", data.filters?.locations || []);
    if (data.currentMonth) {
      const m = document.getElementById("filterMonth");
      if (m && !m.value) m.value = data.currentMonth;
    }
    // Default load with current month
    loadDashboard(getFilters());
  } catch (e) {
    showError("Failed to initialize dashboard: " + e.message);
  }
}

function populateSelect(id, items) {
  const sel = document.getElementById(id);
  if (!sel) return;
  const first = sel.options[0] ? sel.options[0].outerHTML : '<option value="">All</option>';
  sel.innerHTML = first;
  items.forEach(it => {
    const opt = document.createElement("option");
    opt.value = it;
    opt.textContent = it;
    sel.appendChild(opt);
  });
}

async function loadDashboard(filters) {
  showLoader(true);
  try {
    const data = await apiPost("/api/dashboard", filters || {});
    renderDashboard(data);
  } catch (e) {
    showError("Dashboard error: " + e.message);
  } finally {
    showLoader(false);
  }
}

async function loadETM() {
  showLoader(true);
  try {
    const data = await apiGet("/api/etm");
    renderETM(data);
  } catch (e) {
    showError("ETM error: " + e.message);
  } finally {
    showLoader(false);
  }
}

async function loadLive() {
  showLoader(true);
  try {
    const data = await apiPost("/api/live-dashboard", getFilters());
    renderLive(data);
  } catch (e) {
    showError("Live dashboard error: " + e.message);
  } finally {
    showLoader(false);
  }
}

async function loadSlotUtilization() {
  showLoader(true);
  try {
    const data = await apiPost("/api/slot-utilization", getFilters());
    renderSlotUtilization(data);
  } catch (e) {
    showError("Slot utilization error: " + e.message);
  } finally {
    showLoader(false);
  }
}

async function loadAttrition() {
  showLoader(true);
  try {
    const data = await apiPost("/api/attrition", getFilters());
    renderAttrition(data);
  } catch (e) {
    showError("Attrition error: " + e.message);
  } finally {
    showLoader(false);
  }
}

async function searchAnalyst() {
  const email = document.getElementById("searchAnalystEmail")?.value || "";
  if (!email) return;
  showLoader(true);
  try {
    const data = await apiGet(`/api/analyst-search?email=${encodeURIComponent(email)}`);
    renderAnalystSearch(data);
  } catch (e) {
    showError("Analyst search error: " + e.message);
  } finally {
    showLoader(false);
  }
}

function renderDashboard(data) {
  if (!data.success) return;
  setText("currentMonthLabel", data.currentMonth || "");
  renderOverview(data.overview, data);
  renderProductivity(data.productivity);
  renderQuality(data.quality);
  renderPOA(data.poa);
  renderTrends(data.trends);
  renderAlerts(data.alerts);
}

function renderOverview(overview, allData) {
  const m = overview.metrics || {};
  setText("ovTotalTasks", m.totalTasks ?? "-");
  setText("ovAvgAht", m.avgAht ?? "-");
  setText("ovIntFar", m.intFar != null ? m.intFar + "%" : "-");
  setText("ovIntFrr", m.intFrr != null ? m.intFrr + "%" : "-");

  renderTable("tableTL", overview.tlRows || []);
  renderTable("tableAM", overview.amRows || []);
  renderTable("tableAON", overview.aonRows || []);
  renderTable("tableANA", overview.anaRows || []);

  renderBarChart("overviewChart",
    (overview.tlRows || []).map(r => r.TL_Name || r.tl_name || ""),
    (overview.tlRows || []).map(r => parseNumericValue(r.total_task) || 0),
    "Total Tasks",
    false
  );

  const catRows = allData?.productivity?.byCategory || [];
  renderPieChart("overviewPieChart",
    catRows.map(r => r.Category || r.category || ""),
    catRows.map(r => parseNumericValue(r.total_task) || 0),
    "Category Tasks"
  );
}

function renderProductivity(prod) {
  const m = prod.metrics || {};
  setText("prodTotalTasks", m.totalTasks ?? "-");
  setText("prodAvgAht", m.avgAht ?? "-");
  renderTable("tableProdAnalyst", prod.byAnalyst || []);
  renderTable("tableProdTL", prod.byTL || []);
  renderTable("tableProdAM", prod.byAM || []);
  renderTable("tableProdQA", prod.byQA || []);
  renderTable("tableProdCategory", prod.byCategory || []);

  renderBarChart("productivityTLChart",
    (prod.byTL || []).map(r => r.TL_Name || r.tl_name || ""),
    (prod.byTL || []).map(r => parseNumericValue(r.total_task) || 0),
    "Tasks",
    false
  );

  const qaRows = prod.byQA || [];
  const qaCanvas = document.getElementById("productivityQAChart");
  if (qaCanvas && typeof Chart !== "undefined") {
    destroyChart("productivityQAChart");
    chartInstances["productivityQAChart"] = new Chart(qaCanvas.getContext("2d"), {
      type: "bar",
      data: {
        labels: qaRows.map(r => r.QA_Name || r.qa_name || ""),
        datasets: [{
          label: "Tasks",
          data: qaRows.map(r => parseNumericValue(r.total_task) || 0),
          backgroundColor: "rgba(139,92,246,0.6)"
        }]
      },
      options: {
        responsive: true,
        plugins: { legend: { display: true } },
        scales: { x: { stacked: true }, y: { stacked: true, beginAtZero: true } }
      }
    });
  }
}

function renderQuality(q) {
  const m = q.metrics || {};
  setText("qIntFar", m.intFar != null ? m.intFar + "%" : "-");
  setText("qIntFrr", m.intFrr != null ? m.intFrr + "%" : "-");
  setText("qExtFar", m.extFar != null ? m.extFar + "%" : "-");
  setText("qExtFrr", m.extFrr != null ? m.extFrr + "%" : "-");
  setText("qOverallError", m.overallError != null ? m.overallError + "%" : "-");
  renderTable("tableQualAnalyst", q.byAnalyst || []);
  renderTable("tableQualTL", q.byTL || []);
  renderTable("tableQualAM", q.byAM || []);
  renderTable("tableQualQA", q.byQA || []);

  let mis = 0, wrn = 0, clear = 0;
  (q.byAnalyst || []).forEach(r => {
    mis += parseNumericValue(r.mis_fraud) || 0;
    wrn += parseNumericValue(r.wrn_fraud) || 0;
    clear += parseNumericValue(r.total_clear) || 0;
  });
  renderDoughnutChart("qualityDoughnutChart",
    ["Mis Fraud", "WRN Fraud", "Clear"],
    [mis, wrn, clear],
    "Quality Mix"
  );

  const tlRows = q.byTL || [];
  const errCanvas = document.getElementById("qualityErrorChart");
  if (errCanvas && tlRows.length && typeof Chart !== "undefined") {
    destroyChart("qualityErrorChart");
    const palette = ["rgba(239,68,68,0.6)", "rgba(245,158,11,0.6)", "rgba(16,185,129,0.6)", "rgba(59,130,246,0.6)"];
    const keys = Object.keys(tlRows[0] || {});
    const datasets = [];
    keys.forEach(k => {
      if (k === "TL_Name" || k === "tl_name") return;
      const vals = tlRows.map(r => parseNumericValue(r[k]) || 0);
      if (vals.some(v => v !== 0)) {
        datasets.push({
          label: getHeaderLabel(k),
          data: vals,
          backgroundColor: palette[datasets.length % palette.length]
        });
      }
    });
    if (!datasets.length) {
      datasets.push({
        label: "Mis Fraud",
        data: tlRows.map(r => parseNumericValue(r.mis_fraud) || 0),
        backgroundColor: palette[0]
      });
    }
    chartInstances["qualityErrorChart"] = new Chart(errCanvas.getContext("2d"), {
      type: "bar",
      data: {
        labels: tlRows.map(r => r.TL_Name || r.tl_name || ""),
        datasets
      },
      options: {
        responsive: true,
        plugins: { legend: { display: true } },
        scales: { x: { stacked: true }, y: { stacked: true, beginAtZero: true } }
      }
    });
  }
}

function renderPOA(poa) {
  const m = poa.metrics || {};
  setText("poaTasks", m.poaTasks ?? "-");
  setText("poaAvgAht", m.poaAvgAht ?? "-");
  renderTable("tablePOAAnalyst", poa.byAnalyst || []);
  renderTable("tablePOATL", poa.byTL || []);
  renderTable("tablePOAAM", poa.byAM || []);

  renderBarChart("poaChart",
    (poa.byTL || []).map(r => r.TL_Name || r.tl_name || ""),
    (poa.byTL || []).map(r => parseNumericValue(r.poa_task) || 0),
    "POA Tasks",
    false
  );
}

function renderTrends(trends) {
  const ctx = document.getElementById("trendChart");
  if (!ctx) return;
  if (typeof Chart === "undefined") return;
  const rows = trends.rows || [];
  const labels = rows.map(r => r.Date || r.Month || r.date || r.month || "");
  const values = rows.map(r => r.totalTasks || r.Total_Task || 0);
  const ahtValues = rows.map(r => parseNumericValue(r.avgAht) || parseNumericValue(r.Avg_AHT) || parseNumericValue(r.total_aht) || null);
  const datasets = [{
    label: "Total Tasks",
    data: values,
    borderColor: "#3b82f6",
    backgroundColor: "rgba(59,130,246,0.1)",
    fill: true,
    tension: 0.3
  }];
  if (ahtValues.some(v => v != null)) {
    datasets.push({
      label: "AHT",
      data: ahtValues,
      borderColor: "#f59e0b",
      backgroundColor: "rgba(245,158,11,0.1)",
      fill: true,
      tension: 0.3,
      yAxisID: "y1"
    });
  }
  if (chartInstances.trend) chartInstances.trend.destroy();
  chartInstances.trend = new Chart(ctx.getContext("2d"), {
    type: "line",
    data: { labels, datasets },
    options: {
      responsive: true,
      plugins: { legend: { display: true } },
      scales: ahtValues.length > 0 ? {
        y: { type: "linear", display: true, position: "left" },
        y1: { type: "linear", display: true, position: "right", grid: { drawOnChartArea: false } }
      } : {}
    }
  });
}

function renderAlerts(alertsData) {
  const container = document.getElementById("alertsContainer");
  if (!container) return;
  container.innerHTML = "";
  const list = alertsData.alerts || [];
  list.forEach(a => {
    const div = document.createElement("div");
    div.className = `alert alert-${a.type || "warning"}`;
    div.textContent = a.message;
    container.appendChild(div);
  });
}

function renderETM(data) {
  renderTable("tableDocETM", data.etm?.doc_etm || []);
  renderTable("tablePOAETM", data.etm?.poa_etm || []);
  renderTable("tableTaskSkip", data.taskSkip?.task_skip || []);

  renderSimpleBarChart("etmChart", data.etm?.doc_etm || data.etm?.poa_etm || data.taskSkip?.task_skip || []);
}

function renderLive(data) {
  renderTable("tableLive", data.live || []);
  renderSimpleBarChart("liveChart", data.live || []);
}

function renderSlotUtilization(data) {
  renderTable("tableSlotPerf", data.slotWisePerformance || []);
  renderTable("tableUtilization", data.utilization || []);
  renderSimpleBarChart("slotChart", data.utilization || data.slotWisePerformance || []);
}

function renderAttrition(data) {
  renderTable("tableAttrition", data.attrition || []);
  renderSimpleBarChart("attritionChart", data.attrition || []);
}

function renderAnalystSearch(data) {
  const container = document.getElementById("analystResults");
  if (container) {
    container.classList.add("active");
  }
  renderTable("tableAnalystSearch", data.results || []);
}

function escapeHtml(text) {
  if (text == null) return "";
  const div = document.createElement("div");
  div.textContent = text;
  return div.innerHTML;
}

function renderTable(tableId, rows) {
  const table = document.getElementById(tableId);
  if (!table) return;
  const thead = table.querySelector("thead tr");
  const tbody = table.querySelector("tbody");
  tbody.innerHTML = "";
  if (!rows || !rows.length) {
    if (thead) thead.innerHTML = "<th>No data</th>";
    tbody.innerHTML = "<tr><td>No data available</td></tr>";
    return;
  }
  tableOriginalData[tableId] = rows;
  const keys = Object.keys(rows[0]);
  if (thead) {
    thead.innerHTML = keys.map(k =>
      `<th style="cursor:pointer" onclick="sortTable('${tableId}', '${k}')">${escapeHtml(getHeaderLabel(k))}${getSortIndicator(tableId, k)}</th>`
    ).join("");
  }
  rows.forEach(r => {
    const tr = document.createElement("tr");
    tr.innerHTML = keys.map(k => {
      const style = getCellStyle(k, r[k]);
      return `<td${style ? ` style="${style}"` : ""}>${escapeHtml(r[k])}</td>`;
    }).join("");
    tbody.appendChild(tr);
  });
}

function onFiltersApply() {
  const f = getFilters();
  loadDashboard(f);
  if (currentTab === "etm") loadETM();
  if (currentTab === "live") loadLive();
  if (currentTab === "slot") loadSlotUtilization();
  if (currentTab === "attrition") loadAttrition();
}

function onFiltersReset() {
  document.querySelectorAll(".filter-group select").forEach(s => s.value = "");
  document.querySelectorAll(".filter-group input").forEach(i => i.value = "");
  loadDashboard(getFilters());
  if (currentTab === "etm") loadETM();
  if (currentTab === "live") loadLive();
  if (currentTab === "slot") loadSlotUtilization();
  if (currentTab === "attrition") loadAttrition();
}

document.addEventListener("DOMContentLoaded", () => {
  loadInit();

  document.querySelectorAll(".tab").forEach(tab => {
    tab.addEventListener("click", () => {
      switchTab(tab.dataset.target);
      if (tab.dataset.target === "etm") loadETM();
      if (tab.dataset.target === "live") loadLive();
      if (tab.dataset.target === "slot") loadSlotUtilization();
      if (tab.dataset.target === "attrition") loadAttrition();
    });
  });

  document.getElementById("btnApply")?.addEventListener("click", onFiltersApply);
  document.getElementById("btnReset")?.addEventListener("click", onFiltersReset);
  document.getElementById("btnSearchAnalyst")?.addEventListener("click", searchAnalyst);
  document.getElementById("btnDownloadExcel")?.addEventListener("click", exportCurrentTab);
});
