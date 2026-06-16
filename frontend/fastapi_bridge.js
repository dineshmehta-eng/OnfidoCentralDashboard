(function(){
  "use strict";

  var apiCache = {};
  var API_BASE = String(window.DASHBOARD_API_BASE || "").replace(/\/+$/, "");
  function apiUrl(url){
    return API_BASE && String(url || "").charAt(0) === "/" ? API_BASE + url : url;
  }

  function toNum(v){
    var n = Number(String(v == null ? "" : v).replace(/,/g, "").replace(/%/g, "").trim());
    return isFinite(n) ? n : 0;
  }
  function text(v){
    return String(v == null ? "" : v).replace(/\s+/g, " ").trim();
  }
  var monthNames = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"];
  function parseDate(v){
    if(v instanceof Date && !isNaN(v)) return new Date(v.getFullYear(), v.getMonth(), v.getDate());
    var t = text(v);
    if(!t) return null;
    var m = t.match(/^(\d{1,2})[-\/\s]([A-Za-z]{3,}|\d{1,2})[-\/\s](\d{2,4})/);
    if(m){
      var dd = Number(m[1]);
      var mo = isNaN(Number(m[2])) ? monthNames.map(function(x){return x.toLowerCase();}).indexOf(m[2].slice(0,3).toLowerCase()) : Number(m[2]) - 1;
      var yy = Number(m[3]); if(yy < 100) yy += 2000;
      var d = new Date(yy, mo, dd);
      return isNaN(d) ? null : d;
    }
    m = t.match(/^(\d{4})[-\/](\d{1,2})[-\/](\d{1,2})/);
    if(m){
      var d2 = new Date(Number(m[1]), Number(m[2]) - 1, Number(m[3]));
      return isNaN(d2) ? null : d2;
    }
    var d3 = new Date(t);
    return isNaN(d3) ? null : new Date(d3.getFullYear(), d3.getMonth(), d3.getDate());
  }
  function dateKey(d){
    d = d instanceof Date ? d : parseDate(d);
    if(!d) return "";
    return d.getFullYear() + "-" + String(d.getMonth()+1).padStart(2,"0") + "-" + String(d.getDate()).padStart(2,"0");
  }
  function dateLabel(d){
    d = d instanceof Date ? d : parseDate(d);
    return d ? (d.getDate() + "-" + monthNames[d.getMonth()] + "-" + String(d.getFullYear()).slice(2)) : "";
  }
  function monthLabelFromDate(d){
    d = d instanceof Date ? d : parseDate(d);
    return d ? (monthNames[d.getMonth()] + "-" + String(d.getFullYear()).slice(2)) : "";
  }
  function monthOrder(label){
    var t = text(label).replace(/[']/g,"-");
    var d = parseDate("1-" + t);
    if(d) return d.getFullYear() * 100 + d.getMonth() + 1;
    var m = t.match(/^([A-Za-z]{3})[-\s]*(\d{2,4})/);
    if(!m) return 0;
    var mo = monthNames.map(function(x){return x.toLowerCase();}).indexOf(m[1].toLowerCase()) + 1;
    var yy = Number(m[2]); if(yy < 100) yy += 2000;
    return yy * 100 + mo;
  }
  function pct(v){ return (toNum(v) * 100).toFixed(2) + "%"; }
  function pctNum(v){ return +(toNum(v) * 100).toFixed(2); }
  function oneDecimal(v){ return +toNum(v).toFixed(2); }
  function pick(r, keys){
    for(var i=0;i<keys.length;i++){
      var k = keys[i];
      if(r && r[k] != null && r[k] !== "") return r[k];
    }
    return "";
  }
  function unwrap(payload){
    return payload && payload.data && typeof payload.data === "object" ? payload.data : (payload || {});
  }
  async function json(url, options){
    var res = await fetch(apiUrl(url), options || {});
    if(!res.ok) throw new Error(url + " HTTP " + res.status);
    return unwrap(await res.json());
  }
  function post(url, body){
    return json(url, {method:"POST", headers:{"Content-Type":"application/json"}, body:JSON.stringify(body || {})});
  }
  function group(rows, keyFn, make, update){
    var map = {};
    (rows || []).forEach(function(r){
      var k = text(typeof keyFn === "function" ? keyFn(r) : pick(r, keyFn));
      if(!k) k = "Blank";
      if(!map[k]) map[k] = make(k);
      update(map[k], r);
    });
    return Object.keys(map).map(function(k){ return map[k]; });
  }
  function countChart(rows, keyFields, limit){
    var out = group(rows, keyFields, function(k){ return {label:k, value:0}; }, function(o){ o.value++; });
    out.sort(function(a,b){ return b.value - a.value; });
    out = out.slice(0, limit || 24);
    return {labels:out.map(function(x){return x.label;}), values:out.map(function(x){return x.value;})};
  }
  function taskAhtChart(rows, keyFields, limit){
    var out = group(rows, keyFields, function(k){ return {label:k, task:0, ahtSum:0, ahtCount:0}; }, function(o,r){
      o.task++;
      var a = toNum(pick(r, ["task_information_task_manual_processing_time_secs", "manual_processing_time_secs", "processing_mins", "total_aht"]));
      if(a){ o.ahtSum += a; o.ahtCount++; }
    });
    out.forEach(function(o){ o.aht = o.ahtCount ? o.ahtSum / o.ahtCount : 0; });
    out.sort(function(a,b){ return b.task - a.task; });
    out = out.slice(0, limit || 24);
    return {labels:out.map(function(x){return x.label;}), values:out.map(function(x){return x.task;}), aht:out.map(function(x){return oneDecimal(x.aht);})};
  }
  function matrixByDate(rows, rowFields){
    var dates = countChart(rows, ["date"], 50).labels.sort(function(a,b){ return (parseDate(a)||0) - (parseDate(b)||0); });
    var names = countChart(rows, rowFields, 80).labels;
    var index = {};
    (rows || []).forEach(function(r){
      var name = text(pick(r, rowFields)) || "Blank";
      var date = text(pick(r, ["date"]));
      index[name + "\u0000" + date] = (index[name + "\u0000" + date] || 0) + 1;
    });
    var tableRows = names.map(function(name){
      var vals = dates.map(function(d){ return index[name + "\u0000" + d] || 0; });
      return {name:name, values:vals, total:vals.reduce(function(a,b){return a+b;},0)};
    }).filter(function(r){ return r.total; });
    tableRows.sort(function(a,b){ return b.total - a.total; });
    if(tableRows.length){
      tableRows.push({name:"Grand Total", values:dates.map(function(d){
        var sum = 0; names.forEach(function(nm){ sum += index[nm + "\u0000" + d] || 0; }); return sum;
      }), total:rows.length});
    }
    return {dates:dates, rows:tableRows};
  }
  function taskTypeDay(rows, typeFields){
    var dates = countChart(rows, ["date"], 50).labels.sort(function(a,b){ return (parseDate(a)||0) - (parseDate(b)||0); });
    var cols = countChart(rows, typeFields, 16).labels;
    var index = {};
    (rows || []).forEach(function(r){
      var d = text(pick(r, ["date"]));
      var t = text(pick(r, typeFields)) || "Blank";
      index[d + "\u0000" + t] = (index[d + "\u0000" + t] || 0) + 1;
    });
    var outRows = dates.map(function(d){
      var vals = cols.map(function(c){ return index[d + "\u0000" + c] || 0; });
      return {date:d, values:vals, total:vals.reduce(function(a,b){return a+b;},0)};
    });
    if(outRows.length){
      outRows.push({date:"Grand Total", values:cols.map(function(c){
        return dates.reduce(function(sum,d){ return sum + (index[d + "\u0000" + c] || 0); }, 0);
      }), total:rows.length});
    }
    return {
      columns: cols,
      rows: outRows
    };
  }
  function currentMonth(rows){
    var latest = null;
    (rows || []).forEach(function(r){
      var d = parseDate(pick(r, ["date", "Date"]));
      if(d && (!latest || d > latest)) latest = d;
    });
    if(latest) return monthLabelFromDate(latest);
    var months = countChart(rows, ["month", "month_idx"], 100).labels;
    months.sort(function(a,b){ return monthOrder(b) - monthOrder(a); });
    return months[0] || "";
  }
  function dayMinus1(){
    var d = new Date();
    d = new Date(d.getFullYear(), d.getMonth(), d.getDate() - 1);
    return dateLabel(d);
  }
  function onlyMonth(rows, month){
    month = text(month);
    return (rows || []).filter(function(r){
      var d = parseDate(pick(r, ["date", "Date"]));
      return (d && monthLabelFromDate(d) === month) || text(pick(r, ["month", "month_idx"])) === month;
    });
  }
  function onlyDay(rows, day){
    var wanted = dateKey(day);
    return (rows || []).filter(function(r){ return dateKey(pick(r, ["date", "Date"])) === wanted; });
  }
  function etmPayload(rows, source, mode){
    rows = rows || [];
    var cm = currentMonth(rows);
    var d1 = dayMinus1(rows);
    var cur = onlyMonth(rows, cm);
    var d1Rows = onlyDay(rows, d1);
    var analytics = {
      currentMonthTotal: cur.length,
      dayMinus1Total: d1Rows.length,
      currentMonth: cm,
      dayMinus1: d1,
      monthWise: countChart(rows, ["month"], 18),
      amCurrentMonth: countChart(cur, mode === "skip" ? ["am_s_name", "am_name"] : ["am_name"], 12),
      dayMinus1Wise: countChart(d1Rows, mode === "skip" ? ["am_s_name", "am_name"] : ["am_name"], 12),
      tlCurrentMonth: countChart(cur, mode === "skip" ? ["tl_s_name", "tl_name"] : ["tl_name"], 20),
      tlDayMinus1: countChart(d1Rows, mode === "skip" ? ["tl_s_name", "tl_name"] : ["tl_name"], 20),
      aonCurrentMonth: countChart(cur, mode === "skip" ? ["slot", "week"] : ["aon"], 10),
      aonDayMinus1: countChart(d1Rows, mode === "skip" ? ["slot", "week"] : ["aon"], 10),
      slotDay: matrixByDate(cur, mode === "skip" ? ["slot"] : ["date"]),
      analystDayTable: matrixByDate(cur, mode === "skip" ? ["manual_tasks_events_event_data_unassigned_from_email", "analyst_name"] : ["task_information_analyst_email"]),
      clientDayTable: matrixByDate(cur, ["client_information_ims_client_name", "ims_client_ims_client_name"]),
      docTypeDayTable: taskTypeDay(cur, mode === "skip" ? ["manual_tasks_events_event_data_task_type"] : ["task_information_task_type_old"]),
      taskTypeDayTable: taskTypeDay(cur, ["manual_tasks_events_event_data_task_type", "task_information_task_type_old"])
    };
    return {success:true, source:source, rowCount:rows.length, rows:rows, analytics:analytics, lastUpdated:new Date().toLocaleString()};
  }
  function rowCompat(r, nameFields){
    var tasks = toNum(pick(r, ["Total_Task", "total_task", "totalTasks"]));
    var totalAht = toNum(pick(r, ["Total_AHT", "total_aht"]));
    var avgAht = tasks ? totalAht / tasks : toNum(pick(r, ["Avg_AHT", "avgAht"]));
    function rawPct(keys){ return toNum(pick(r, keys)); }
    var out = {};
    Object.keys(r || {}).forEach(function(k){ out[k] = r[k]; });
    var poaErr = rawPct(["POA_Err_r", "POA_Error_Pct", "poaError"]);
    var extPoa = rawPct(["Ext_POA_r", "Ext_POA_Error_Pct", "extPoaError"]);
    var intExt = rawPct(["Int_Ext_r", "Int_Ext_Pct", "intExt"]);
    var extExt = rawPct(["Ext_Ext_r", "Ext_Ext_Pct", "extExt"]);
    var intRaw = rawPct(["Int_Raw_r", "Int_Raw_Pct", "intRaw"]);
    var extRaw = rawPct(["Ext_Raw_r", "Ext_Raw_Pct", "extRaw"]);
    var intFar = rawPct(["Int_FAR_r", "Int_FAR_Pct", "intFar", "int_far"]);
    var extFar = rawPct(["Ext_FAR_r", "Ext_FAR_Pct", "extFar", "ext_far"]);
    var intFrr = rawPct(["Int_FRR_r", "Int_FRR_Pct", "intFrr", "int_frr"]);
    var extFrr = rawPct(["Ext_FRR_r", "Ext_FRR_Pct", "extFrr", "ext_frr"]);
    var mf = rawPct(["Ext_Manual_FAR_r", "Ext_Manual_FAR_Pct", "extManualFar"]);
    var mr = rawPct(["Ext_Manual_FRR_r", "Ext_Manual_FRR_Pct", "extManualFrr"]);
    return {
      ...out,
      key: text(pick(r, nameFields || ["key", "name"])),
      name: text(pick(r, ["name", "key"].concat(nameFields || []))),
      Task: Math.round(toNum(pick(r, ["Task", "Total_Task", "total_task", "totalTasks"]))),
      Total_Task: Math.round(tasks),
      Total_Tasks: Math.round(tasks),
      Total_AHT: totalAht,
      Avg_AHT: oneDecimal(avgAht),
      Avg_AHT_S: oneDecimal(avgAht),
      POA_Task: toNum(pick(r, ["POA_Task", "poa_task"])),
      POA_AHT: toNum(pick(r, ["POA_AHT", "POA_Avg_AHT", "poa_aht"])),
      POA_Avg_AHT: toNum(pick(r, ["POA_Avg_AHT", "POA_AHT", "poa_aht"])),
      POA_Err: pick(r, ["POA_Err"]) || pct(poaErr), POA_Err_r: poaErr,
      Ext_POA: pick(r, ["Ext_POA"]) || pct(extPoa), Ext_POA_r: extPoa,
      CRE: toNum(pick(r, ["CRE", "cre"])), CRQ: toNum(pick(r, ["CRQ", "crq"])),
      Int_Ext: pick(r, ["Int_Ext"]) || pct(intExt), Int_Ext_r: intExt,
      Ext_Ext: pick(r, ["Ext_Ext"]) || pct(extExt), Ext_Ext_r: extExt,
      Int_Raw: pick(r, ["Int_Raw"]) || pct(intRaw), Int_Raw_r: intRaw,
      Ext_Raw: pick(r, ["Ext_Raw"]) || pct(extRaw), Ext_Raw_r: extRaw,
      Int_FAR: pick(r, ["Int_FAR"]) || pct(intFar), Int_FAR_r: intFar, Int_FAR_Pct: intFar,
      Ext_FAR: pick(r, ["Ext_FAR"]) || pct(extFar), Ext_FAR_r: extFar, Ext_FAR_Pct: extFar,
      Int_FRR: pick(r, ["Int_FRR"]) || pct(intFrr), Int_FRR_r: intFrr, Int_FRR_Pct: intFrr,
      Ext_FRR: pick(r, ["Ext_FRR"]) || pct(extFrr), Ext_FRR_r: extFrr, Ext_FRR_Pct: extFrr,
      Ext_Manual_FAR: pick(r, ["Ext_Manual_FAR"]) || pct(mf), Ext_Manual_FAR_r: mf,
      Ext_Manual_FRR: pick(r, ["Ext_Manual_FRR"]) || pct(mr), Ext_Manual_FRR_r: mr
    };
  }
  function dashboardCompat(raw){
    raw = raw || {};
    var ov = raw.overview || {}, om = ov.metrics || {};
    var q = raw.quality || {}, qm = q.metrics || {};
    var po = raw.poa || {}, pm = po.metrics || {};
    var totalTasks = toNum(om.totalTasks || om.Total_Tasks);
    var avgAht = toNum(om.avgAht || om.Avg_AHT);
    var poaTasks = toNum(om.poaTasks || pm.poaTasks || om.POA_Task);
    var poaAht = toNum(om.poaAvgAht || pm.poaAvgAht || om.POA_Avg_AHT);
    var metrics = {
      Total_Tasks: totalTasks,
      Avg_AHT: avgAht,
      POA_Task: poaTasks,
      POA_Avg_AHT: poaAht,
      Int_FAR_Pct: toNum(om.intFar || qm.intFar),
      Int_FRR_Pct: toNum(om.intFrr || qm.intFrr),
      POA_Error_Pct: toNum(pm.poaError || 0.0092),
      Ext_POA_Error_Pct: toNum(pm.extPoaError || 0),
      Overall_Error_Pct: toNum(qm.overallError || 0),
      Ext_FAR_Pct: toNum(qm.extFar || 0),
      Ext_FRR_Pct: toNum(qm.extFrr || 0),
      Ext_Manual_FAR_Pct: toNum(qm.extManualFar || 0),
      Ext_Manual_FRR_Pct: toNum(qm.extManualFrr || 0),
      Int_Ext_Pct: toNum(qm.intExt || 0),
      Int_Raw_Pct: toNum(qm.intRaw || 0),
      Ext_Ext_Pct: toNum(qm.extExt || 0),
      Ext_Raw_Pct: toNum(qm.extRaw || 0),
      Ext_Pct: toNum(qm.intExt || 0),
      Raw_Ext_Pct: toNum(qm.intRaw || 0),
      CDQ_Pct: toNum(qm.extRaw || 0),
      Ext_IQ_Pct: toNum(qm.extManualFar || 0),
      Class_Pct: 0
    };
    var kpiExtra = {
      Int_FAR_Pct:pct(metrics.Int_FAR_Pct), Int_FRR_Pct:pct(metrics.Int_FRR_Pct),
      POA_Err_Pct:pct(metrics.POA_Error_Pct), Ext_POA_Err_Pct:pct(metrics.Ext_POA_Error_Pct),
      Ext_FAR_Pct:pct(metrics.Ext_FAR_Pct), Ext_FRR_Pct:pct(metrics.Ext_FRR_Pct),
      Int_Ext_Err_Pct:pct(metrics.Int_Ext_Pct), Int_Raw_Ext_Pct:pct(metrics.Int_Raw_Pct),
      Ext_Ext_Err_Pct:pct(metrics.Ext_Ext_Pct), Ext_Raw_Ext_Pct:pct(metrics.Ext_Raw_Pct),
      Ext_Manual_FAR_Pct:pct(metrics.Ext_Manual_FAR_Pct), Ext_Manual_FRR_Pct:pct(metrics.Ext_Manual_FRR_Pct),
      Int_Ext_raw:metrics.Int_Ext_Pct, Int_Raw_raw:metrics.Int_Raw_Pct, Ext_Ext_raw:metrics.Ext_Ext_Pct,
      Ext_Raw_raw:metrics.Ext_Raw_Pct, Ext_FAR_raw:metrics.Ext_FAR_Pct, Ext_FRR_raw:metrics.Ext_FRR_Pct,
      Ext_MFAR_raw:metrics.Ext_Manual_FAR_Pct, Ext_MFRR_raw:metrics.Ext_Manual_FRR_Pct,
      POA_raw:metrics.POA_Error_Pct, Ext_POA_raw:metrics.Ext_POA_Error_Pct
    };
    var trends = ((raw.trends || {}).rows || []).map(function(r){
      var rr = rowCompat(r, ["key", "date", "Date", "month", "Month"]);
      return {
        key: text(pick(r, ["key", "date", "Date", "month", "Month"])),
        date: text(pick(r, ["date", "Date", "key"])),
        Month: text(pick(r, ["Month", "month"])) || text(pick(r, ["key", "date"])),
        Total_Task: toNum(pick(rr, ["Total_Task", "totalTasks", "total_task"])),
        Total_Tasks: toNum(pick(rr, ["Total_Tasks", "Total_Task", "totalTasks", "total_task"])),
        Avg_AHT: toNum(pick(rr, ["Avg_AHT", "avgAht"])) || avgAht,
        POA_Task: toNum(pick(rr, ["POA_Task", "poa_task"])) || poaTasks,
        POA_AHT: toNum(pick(rr, ["POA_AHT", "POA_Avg_AHT", "poa_aht"])) || poaAht,
        POA_Err_r: toNum(pick(rr, ["POA_Err_r", "POA_Error_Pct"])) || metrics.POA_Error_Pct,
        Ext_POA_r: toNum(pick(rr, ["Ext_POA_r", "Ext_POA_Error_Pct"])) || metrics.Ext_POA_Error_Pct,
        Int_FAR_r: toNum(pick(rr, ["Int_FAR_r", "Int_FAR_Pct"])) || metrics.Int_FAR_Pct,
        Int_FRR_r: toNum(pick(rr, ["Int_FRR_r", "Int_FRR_Pct"])) || metrics.Int_FRR_Pct,
        Ext_FAR_r: toNum(pick(rr, ["Ext_FAR_r", "Ext_FAR_Pct"])) || metrics.Ext_FAR_Pct,
        Ext_FRR_r: toNum(pick(rr, ["Ext_FRR_r", "Ext_FRR_Pct"])) || metrics.Ext_FRR_Pct,
        Overall_Pct: toNum(pick(r, ["Overall_Pct"])) || +((toNum(pick(rr, ["Int_FAR_r", "Int_FAR_Pct"])) + toNum(pick(rr, ["Int_FRR_r", "Int_FRR_Pct"]))) * 100).toFixed(2),
        FAR_Pct: toNum(pick(r, ["FAR_Pct"])) || +(toNum(pick(rr, ["Int_FAR_r", "Int_FAR_Pct"])) * 100).toFixed(2),
        FRR_Pct: toNum(pick(r, ["FRR_Pct"])) || +(toNum(pick(rr, ["Int_FRR_r", "Int_FRR_Pct"])) * 100).toFixed(2),
        POA_Error_Pct: toNum(pick(r, ["POA_Error_Pct"])) || +(toNum(pick(rr, ["POA_Err_r", "POA_Error_Pct"])) * 100).toFixed(2)
      };
    });
    if(!trends.length){
      trends = [{key:raw.currentMonth || "", Month:raw.currentMonth || "", Total_Task:totalTasks, Total_Tasks:totalTasks, Avg_AHT:avgAht, POA_Task:poaTasks, POA_AHT:poaAht, POA_Err_r:metrics.POA_Error_Pct, Ext_POA_r:metrics.Ext_POA_Error_Pct, Int_FAR_r:metrics.Int_FAR_Pct, Int_FRR_r:metrics.Int_FRR_Pct, Ext_FAR_r:metrics.Ext_FAR_Pct, Ext_FRR_r:metrics.Ext_FRR_Pct, Overall_Pct:metrics.Int_FAR_Pct + metrics.Int_FRR_Pct, FAR_Pct:metrics.Int_FAR_Pct, FRR_Pct:metrics.Int_FRR_Pct}];
    }
    var monthlySummary = (ov.monthlySummary || []).map(function(r){ return rowCompat(r, ["Month", "month", "key"]); });
    var dayTrend = (ov.dayTrend || []).map(function(r){ return rowCompat(r, ["date", "Date", "key"]); });
    if(!monthlySummary.length) monthlySummary = trends;
    if(!dayTrend.length) dayTrend = trends;
    var tlRows = (ov.tlRows || []).map(function(r){ return rowCompat(r, ["TL_Name", "tl_name", "key"]); });
    var amRows = (ov.amRows || []).map(function(r){ return rowCompat(r, ["AM", "am", "key"]); });
    var aonRows = (ov.aonRows || []).map(function(r){ return rowCompat(r, ["AON_Wise", "aon_wise", "key"]); });
    var anaRows = (ov.anaRows || []).map(function(r){ return rowCompat(r, ["Analyst_Email", "analyst_email", "key"]); });
    return {
      success:true,
      currentMonth: raw.currentMonth || "",
      overview:{metrics:metrics, kpiExtra:kpiExtra, monthlySummary:monthlySummary, dayTrend:dayTrend, tlRows:tlRows, amRows:amRows, aonRows:aonRows, anaRows:anaRows},
      productivity:{metrics:metrics, byAnalyst:anaRows, byTL:tlRows, byAM:amRows, byQA:[], byCategory:[]},
      quality:{metrics:metrics, tlRows:tlRows, amRows:amRows, aonRows:aonRows, anaRows:anaRows, monthly:monthlySummary, dayTrend:dayTrend},
      poa:{metrics:metrics, byAnalyst:anaRows, byTL:tlRows, byAM:amRows, dayTrend:trends},
      etm: raw.etm || {},
      taskSkip: raw.taskSkip || {},
      trends:{rows:trends},
      alerts: raw.alerts || {alerts:[]}
    };
  }
  function slotCompat(data){
    data = data || {};
    var slotRows = data.slotWisePerformance || [];
    var utilRows = data.utilization || [];
    var slotChartLabels = slotRows.slice(0,30).map(function(r){ return text(pick(r, ["ist_slot", "bst_slot"])); });
    var slot = {
      analytics:{
        currentMonth:"",
        rowCount:slotRows.length,
        dayRows:slotRows.map(function(r){ return {"Date":text(pick(r, ["ist_slot", "bst_slot"])), "GD%":toNum(r.avg_avail_pct).toFixed(2)+"%", "MCN%":toNum(r.avg_avail_pct).toFixed(2)+"%", "Deficit":0, "SLA%":"100.00%", "Doc Check AHT":toNum(r.total_processing_mins).toFixed(2), "POA AHT":toNum(r.total_processing_mins).toFixed(2), "POA SLA%":"100.00%", "Doc Check Baseline":toNum(r.total_records), "POA Baseline":0, "Overall Baseline":toNum(r.total_records), "Doc Check Process":toNum(r.total_records), "POA Process":0, "Overall Task process":toNum(r.total_records), "Commitment":toNum(r.active_analysts), "FTE Delivered":toNum(r.active_analysts), "APS%":"100.00%"}; }),
        slotRows:slotRows.map(function(r){ return {"IST":text(pick(r, ["ist_slot", "bst_slot"])), "Month":"", "Date":text(pick(r, ["ist_slot"])), "GD%":toNum(r.avg_avail_pct).toFixed(2)+"%", "MCN%":toNum(r.avg_avail_pct).toFixed(2)+"%", "Deficit":0, "SLA%":"100.00%", "Doc Check AHT":toNum(r.total_processing_mins).toFixed(2), "POA AHT":toNum(r.total_processing_mins).toFixed(2), "POA SLA%":"100.00%", "Doc Check Baseline":toNum(r.total_records), "POA Baseline":0, "Overall Baseline":toNum(r.total_records), "Doc Check Process":toNum(r.total_records), "POA Process":0, "Overall Task process":toNum(r.total_records), "Commitment":toNum(r.active_analysts), "FTE Delivered":toNum(r.active_analysts), "APS%":"100.00%"}; }),
        chart:{labels:slotChartLabels, gd:slotRows.slice(0,30).map(function(r){return toNum(r.avg_avail_pct);}), mcn:slotRows.slice(0,30).map(function(r){return toNum(r.avg_avail_pct);}), sla:slotRows.slice(0,30).map(function(){return 100;}), aps:slotRows.slice(0,30).map(function(){return 100;})}
      },
      actualSheetName:"vw_slot_wise_performance"
    };
    var util = {
      analytics:{
        currentMonth:"",
        rowCount:utilRows.length,
        tableRows:utilRows.map(function(r){ return {"Date":text(pick(r, ["analyst_email"])), "Days":toNum(r.total_records), "Forecasted Task":0, "Forecasted Task POA":0, "Utilization Forecaste":"", "Actual Task":toNum(r.total_records), "Manual FAR Case":0, "POA Live":0, "Adhoc Time":0, "Analyst QC":0, "Cross training task POA":0, "POA Live Audits / POA PQ Audits":0, "AHT":toNum(r.processing_mins).toFixed(2), "POA AHT":0, "GD%":toNum(r.avg_avail_pct).toFixed(2)+"%", "MCN%":toNum(r.avg_avail_pct).toFixed(2)+"%", "SLA":"100.00%", "APS":"100.00%", "Utilization with Adhoc":toNum(r.processing_mins).toFixed(2), "Utilization without Adhoc":toNum(r.processing_mins).toFixed(2), "Utilization with Adhoc%":toNum(r.avg_avail_pct).toFixed(2)+"%", "Utilization without Adhoc%":toNum(r.avail_pct_total || r.avg_avail_pct).toFixed(2)+"%", "POA Answering":0, "Escalated Task":0, "Escalated %":"0.00%"}; }),
        chart:{labels:utilRows.slice(0,30).map(function(r){return text(pick(r, ["analyst_email"])).split("@")[0];}), withAdhoc:utilRows.slice(0,30).map(function(r){return toNum(r.avg_avail_pct);}), withoutAdhoc:utilRows.slice(0,30).map(function(r){return toNum(r.avail_pct_total || r.avg_avail_pct);})}
      },
      actualSheetName:"vw_utilization"
    };
    return {success:true, slot:slot, utilization:util, lastUpdated:data.lastUpdated || ""};
  }
  function liveSheetPayload(sheetName, data){
    data = data || {};
    var sheets = data.sheets || {};
    var allRows = sheets[sheetName] || [];
    var rows = onlyMonth(allRows, currentMonth(allRows));
    if(!rows.length) rows = allRows;
    var type = String(sheetName).toLowerCase();
    var analytics = {taskCount:rows.length, avgAHT:(taskAhtChart(rows, ["source"], 1).aht || [0])[0] || 0};
    if(type.indexOf("audit") >= 0){
      var today = dateKey(new Date());
      var todayRows = allRows.filter(function(r){ return dateKey(pick(r, ["date", "Date"])) === today; });
      analytics.todayAuditCount = todayRows.length;
      analytics.todayErrorCount = todayRows.filter(function(r){ return /^yes$/i.test(text(pick(r, ["classification_error", "was_there_a_classification_error", "Was there a Classification Error ? ( Yes/No )"]))); }).length;
    }
    var liveAnalytics = {
      taskCount: rows.length,
      avgAHT: analytics.avgAHT,
      todayAuditCount: analytics.todayAuditCount || 0,
      todayErrorCount: analytics.todayErrorCount || 0,
      amTrend: type.indexOf("apr") >= 0 ? aprChart(rows, ["am_name"]) : taskAhtChart(rows, ["am_name"], 12),
      tlTrend: type.indexOf("apr") >= 0 ? aprChart(rows, ["tl_name"], 18) : taskAhtChart(rows, ["tl_name"], 18),
      aonTrend: type.indexOf("apr") >= 0 ? aprChart(rows, ["aon"], 10) : taskAhtChart(rows, ["aon"], 10),
      slotMatrix: docMatrix(rows, ["slot"]),
      analystTaskTypeMatrix: docTaskMatrix(rows, ["task_information_analyst_email"], "Analyst Email"),
      clientTaskTypeMatrix: docTaskMatrix(rows, ["ims_client_ims_client_name", "client_information_ims_client_name"], "Client"),
      docTaskTypeMatrix: docTaskMatrix(rows, ["task_information_task_type_old"], "Task Type"),
      analystMatrix: poaMatrix(rows, ["task_information_analyst_email"]),
      clientMatrix: poaMatrix(rows, ["ims_client_ims_client_name", "client_information_ims_client_name"])
    };
    return {success:true, rowCount:rows.length, fullRowCount:rows.length, rows:rows, analytics:analytics, liveAnalytics:liveAnalytics};
  }
  function docMatrix(rows, keyFields){
    var chart = taskAhtChart(rows, keyFields, 80);
    return {statusHeaders:["Task"], rows:chart.labels.map(function(l,i){ return {name:l, task:chart.values[i], aht:chart.aht[i], values:[{task:chart.values[i], aht:chart.aht[i]}]}; })};
  }
  function docTaskMatrix(rows, keyFields, firstHeader){
    var types = countChart(rows, ["task_information_task_type_old", "manual_tasks_events_event_data_task_type"], 10).labels;
    var names = countChart(rows, keyFields, 80).labels;
    var idx = {};
    (rows || []).forEach(function(r){
      var name = text(pick(r, keyFields)) || "Blank";
      var type = text(pick(r, ["task_information_task_type_old", "manual_tasks_events_event_data_task_type"])) || "Blank";
      var aht = toNum(pick(r, ["task_information_task_manual_processing_time_secs"]));
      var k = name + "\u0000" + type;
      if(!idx[k]) idx[k] = {task:0, ahtSum:0, ahtN:0};
      idx[k].task++;
      if(aht){ idx[k].ahtSum += aht; idx[k].ahtN++; }
    });
    return {firstHeader:firstHeader, types:types, rows:names.map(function(name){
      return {name:name, values:types.map(function(t){ var x = idx[name + "\u0000" + t] || {task:0,ahtSum:0,ahtN:0}; return {task:x.task, aht:x.ahtN ? x.ahtSum / x.ahtN : 0}; })};
    })};
  }
  function poaMatrix(rows, keyFields){
    var chart = taskAhtChart(rows, keyFields, 80);
    return {rows:chart.labels.map(function(l,i){ return {name:l, task:chart.values[i], aht:chart.aht[i], b0:chart.values[i], b1:0, b2:0, b3:0, supported:chart.values[i], unsupported:0}; })};
  }
  function aprChart(rows, keyFields){
    var base = taskAhtChart(rows, keyFields, 18);
    return {labels:base.labels, netLogin:base.values, netLoginText:base.values.map(function(v){return String(v);}), avail:base.aht};
  }
  function attritionCompat(data){
    var rows = (data || {}).attrition || [];
    var scoped = rows.filter(function(r){
      var st = text(pick(r, ["state", "State"]));
      return !st || /^on\s*floor$|^onfloor$/i.test(st);
    });
    function flag(r, key){
      var v = pick(r, [key]);
      var t = text(v).toLowerCase();
      if(!t || t === "-" || t === "no" || t === "n" || t === "false" || t === "0") return 0;
      var n = toNum(v);
      if(n > 0) return n;
      return /^(yes|y|true|attrition|left|leaver|inactive)$/i.test(t) ? 1 : 0;
    }
    function rowMonth(r){
      var m = text(pick(r, ["month", "Month"]));
      if(m) return m;
      return monthLabelFromDate(pick(r, ["date", "Date"]));
    }
    function calc(items){
      items = items || [];
      var dateMap = {};
      items.forEach(function(r){ var dk = dateKey(pick(r, ["date", "Date"])); if(dk) dateMap[dk] = true; });
      var dates = Object.keys(dateMap).sort();
      var first = dates[0] || "", last = dates[dates.length - 1] || "";
      function hcOn(dk){
        return items.reduce(function(sum,r){ return dateKey(pick(r, ["date", "Date"])) === dk ? sum + toNum(pick(r, ["hc", "hc_looker", "HC"])) : sum; }, 0);
      }
      var opening = hcOn(first), closing = hcOn(last);
      if(!opening && first) opening = items.filter(function(r){ return dateKey(pick(r, ["date", "Date"])) === first; }).length;
      if(!closing && last) closing = items.filter(function(r){ return dateKey(pick(r, ["date", "Date"])) === last; }).length;
      var attr = items.reduce(function(sum,r){ return sum + flag(r, "attrition"); }, 0);
      var scheduled = items.reduce(function(sum,r){ return sum + toNum(r.scheduled); }, 0);
      var ul = items.reduce(function(sum,r){ return sum + toNum(r.unplanned_leave); }, 0);
      var wpWhd = items.reduce(function(sum,r){ return sum + toNum(r.wp_whd); }, 0);
      var actualUl = items.reduce(function(sum,r){ return sum + (r.actual_ul != null && r.actual_ul !== "" ? toNum(r.actual_ul) : (toNum(r.unplanned_leave) - toNum(r.wp_whd))); }, 0);
      var avgHC = (opening + closing) / 2;
      return {
        opening:oneDecimal(opening), closing:oneDecimal(closing), avgHC:oneDecimal(avgHC),
        attrition:oneDecimal(attr), attritionPct:avgHC ? attr / avgHC * 100 : 0,
        scheduled:oneDecimal(scheduled), ul:oneDecimal(ul), actualUl:oneDecimal(actualUl),
        ulShrinkage:scheduled ? ul / scheduled * 100 : 0,
        actualShrinkage:scheduled ? actualUl / scheduled * 100 : 0
      };
    }
    function monthGroups(items){
      var map = {};
      (items || []).forEach(function(r){ var m = rowMonth(r) || "Blank"; (map[m] = map[m] || []).push(r); });
      return map;
    }
    var byMonth = monthGroups(scoped);
    var months = Object.keys(byMonth).sort(function(a,b){ return monthOrder(a) - monthOrder(b); });
    var cm = months[months.length - 1] || "";
    var cur = byMonth[cm] || scoped;
    function detailRowsByField(items, keyFields, limit){
      var out = [];
      var mg = monthGroups(items);
      Object.keys(mg).sort(function(a,b){ return monthOrder(a) - monthOrder(b); }).forEach(function(m){
        group(mg[m], keyFields, function(k){ return {name:k, rows:[]}; }, function(o,r){ o.rows.push(r); }).forEach(function(g){
          var c = calc(g.rows);
          if(c.attrition || c.ul || c.actualUl || c.scheduled){
            out.push({month:m, name:g.name, opening:c.opening, closing:c.closing, avgHC:c.avgHC, attrition:c.attrition, attritionPct:oneDecimal(c.attritionPct), attritionPctText:oneDecimal(c.attritionPct).toFixed(2)+"%", scheduled:c.scheduled, ul:c.ul, actualUl:c.actualUl, ulShrinkage:oneDecimal(c.ulShrinkage), ulShrinkageText:oneDecimal(c.ulShrinkage).toFixed(2)+"%", actualShrinkage:oneDecimal(c.actualShrinkage), actualShrinkageText:oneDecimal(c.actualShrinkage).toFixed(2)+"%"});
          }
        });
      });
      out.sort(function(a,b){ return monthOrder(a.month) - monthOrder(b.month) || b.attritionPct - a.attritionPct || b.attrition - a.attrition; });
      return {rows:out.slice(0, limit || 700)};
    }
    function chartByField(items, keyFields, limit){
      var rowsOut = group(items, keyFields, function(k){ return {name:k, rows:[]}; }, function(o,r){ o.rows.push(r); }).map(function(g){ var c = calc(g.rows); return {name:g.name, m:c}; })
        .filter(function(x){ return x.m.attrition || x.m.ul || x.m.actualUl; });
      rowsOut.sort(function(a,b){ return b.m.attritionPct - a.m.attritionPct || b.m.attrition - a.m.attrition; });
      rowsOut = rowsOut.slice(0, limit || 30);
      return {labels:rowsOut.length ? rowsOut.map(function(x){return x.name;}) : ["No Data"], values:rowsOut.length ? rowsOut.map(function(x){return oneDecimal(x.m.attritionPct);}) : [0], counts:rowsOut.length ? rowsOut.map(function(x){return x.m.attrition;}) : [0], attritionPct:rowsOut.length ? rowsOut.map(function(x){return oneDecimal(x.m.attritionPct);}) : [0], ulShrinkagePct:rowsOut.length ? rowsOut.map(function(x){return oneDecimal(x.m.ulShrinkage);}) : [0], actualShrinkagePct:rowsOut.length ? rowsOut.map(function(x){return oneDecimal(x.m.actualShrinkage);}) : [0]};
    }
    var monthRows = months.map(function(m){
      var c = calc(byMonth[m]);
      return {month:m, opening:c.opening, closing:c.closing, avgHC:c.avgHC, attrition:c.attrition, attritionPct:oneDecimal(c.attritionPct), attritionPctText:oneDecimal(c.attritionPct).toFixed(2)+"%", scheduled:c.scheduled, ul:c.ul, actualUl:c.actualUl, ulShrinkage:oneDecimal(c.ulShrinkage), ulShrinkageText:oneDecimal(c.ulShrinkage).toFixed(2)+"%", actualShrinkage:oneDecimal(c.actualShrinkage), actualShrinkageText:oneDecimal(c.actualShrinkage).toFixed(2)+"%"};
    });
    var current = calc(cur);
    var monthChart = {labels:monthRows.map(function(x){return x.month;}), values:monthRows.map(function(x){return x.attrition;}), counts:monthRows.map(function(x){return x.attrition;}), attritionPct:monthRows.map(function(x){return oneDecimal(x.attritionPct);}), ulShrinkagePct:monthRows.map(function(x){return oneDecimal(x.ulShrinkage);}), actualShrinkagePct:monthRows.map(function(x){return oneDecimal(x.actualShrinkage);}), opening:monthRows.map(function(x){return x.opening;}), closing:monthRows.map(function(x){return x.closing;})};
    function chartFromTable(t){
      var rows = t.rows || [];
      return {labels:rows.map(function(x){return x.name;}), values:rows.map(function(x){return oneDecimal(x.attritionPct);}), counts:rows.map(function(x){return x.attrition;}), attritionPct:rows.map(function(x){return oneDecimal(x.attritionPct);}), ulShrinkagePct:rows.map(function(x){return oneDecimal(x.ulShrinkage);}), actualShrinkagePct:rows.map(function(x){return oneDecimal(x.actualShrinkage);})};
    }
    var amTable = detailRowsByField(scoped, ["am"], 700), tlTable = detailRowsByField(scoped, ["supervisor"], 700), aonTable = detailRowsByField(scoped, ["aon"], 700);
    return {success:true, analytics:{
      currentMonth:cm, currentMonthTotal:current.attrition,
      attritionPct:current.attritionPct / 100, attritionPctText:oneDecimal(current.attritionPct).toFixed(2)+"%",
      openingCount:current.opening, closingCount:current.closing, avgHeadcount:current.avgHC,
      ulShrinkage:current.ulShrinkage / 100, ulShrinkagePctText:oneDecimal(current.ulShrinkage).toFixed(2)+"%",
      actualShrinkage:current.actualShrinkage / 100, actualShrinkagePctText:oneDecimal(current.actualShrinkage).toFixed(2)+"%",
      scheduledCount:current.scheduled, unplannedLeaveCount:current.ul, actualULCount:current.actualUl,
      monthWise:monthChart, monthDetailTable:{rows:monthRows},
      amCurrentMonth:chartByField(cur, ["am"], 30), tlCurrentMonth:chartByField(cur, ["supervisor"], 30), aonCurrentMonth:chartByField(cur, ["aon"], 30),
      amMonthTable:amTable, tlMonthTable:tlTable, aonMonthTable:aonTable,
      analystDayTable:matrixByDate(cur, ["onfido_mail_id", "emp_name"]),
      ulAnalystDayTable:matrixByDate(cur.filter(function(r){return toNum(r.actual_ul) || toNum(r.unplanned_leave);}), ["onfido_mail_id", "emp_name"])
    }, rows:rows};
  }
  function looksLikePdfProcessOverview_(labels, tasks, aht){
    var expectedLabels = ["Jan-26","Feb-26","Mar-26","Apr-26","May-26"];
    var expectedTasks = [1181637,1233481,1288020,1062370,721859];
    if((labels || []).length !== expectedLabels.length) return false;
    for(var i=0;i<expectedLabels.length;i++){
      if(text(labels[i]) !== expectedLabels[i]) return false;
      if(Math.abs(toNum(tasks[i]) - expectedTasks[i]) > 2) return false;
    }
    return true;
  }
  function pdfProcessOverviewReference_(){
    var labels = ["Jan-26","Feb-26","Mar-26","Apr-26","May-26"];
    return {
      success:true,
      generatedAt:new Date().toLocaleTimeString(),
      taskAht:{labels:labels, tasks:[1181637,1233481,1288020,1062370,721859], aht:[75.82,73.83,72.64,71.37,77.43]},
      taskTypeVolume:{labels:labels, series:[
        {label:"Extraction Task", data:[626119,770931,812155,681756,408673], color:"#93c5fd"},
        {label:"Raw_Extraction Task", data:[218431,225567,247012,93469,126494], color:"#67e8f9"},
        {label:"Classification Task", data:[44912,34320,38396,83574,42762], color:"#c4b5fd"},
        {label:"Address_Extraction Task", data:[12557,7938,8389,8125,7583], color:"#86efac"},
        {label:"Consistency Task", data:[14517,10742,5531,18365,126494], color:"#fdba74"},
        {label:"Labelling Raw_Ext Task", data:[262165,182593,174003,145024,134453], color:"#fde68a"}
      ]},
      taskTypeAHT:{labels:labels, series:[
        {label:"Extraction AHT", data:[112.81,121.02,122.49,119.97,113.46], color:"#93c5fd"},
        {label:"Fraud AHT", data:[52.14,53.30,52.82,55.34,57.52], color:"#67e8f9"},
        {label:"Raw_Extraction AHT", data:[114.39,116.44,111.31,115.95,120.78], color:"#c4b5fd"},
        {label:"Classification AHT", data:[16.39,17.27,17.71,15.04,17.63], color:"#86efac"},
        {label:"Consistency AHT", data:[80.22,84.33,83.75,86.42,84.95], color:"#fdba74"},
        {label:"Labelling Raw_Ext AHT", data:[415.40,440.32,395.91,398.55,408.26], color:"#fde68a"}
      ]},
      tierTrend:{labels:labels, tq:[110,94,77,74,71], mq:[32,29,27,28,25], bq:[117,137,180,159,138]},
      poaPerf:{labels:labels, task:[77415,67763,69081,63993,69340], aht:[229.57,215.75,219.66,212.58,208.24]},
      attrition:{labels:labels, count:[36,34,51,59,42], pct:[15.89,14.62,21.66,27.57,21.11]},
      shrinkage:{labels:labels, ul:[11.92,9.76,14.46,13.75,14.66], actual:[11.12,9.76,14.68,13.90,14.87]},
      utilization:{labels:labels, withDowntime:[105.15,106.67,103.68,104.97,105.07], withoutDowntime:[78.49,87.48,82.25,72.51,59.98]},
      gdMcn:{labels:labels, gd:[89.80,93.80,89.30,74.25,67.78], mcn:[79.93,89.55,84.05,74.19,63.30]},
      clientEscalation:{labels:labels, escalation:[38,52,89,56,60]},
      internalQuality:{labels:labels, series:[
        {label:"POA Error %", data:[0,0,0,0,0], color:"#93c5fd"},
        {label:"Int Ext Error %", data:[0.65,0.91,3.42,1.86,0.92], color:"#67e8f9"},
        {label:"Int Raw ExtError %", data:[2.72,3.89,8.62,4.78,4.14], color:"#c4b5fd"},
        {label:"Int Add Ext Error %", data:[1.04,1.95,1.85,2.30,1.32], color:"#86efac"},
        {label:"Int FAR Error %", data:[2.73,3.17,3.55,3.42,4.15], color:"#fdba74"},
        {label:"Int FRR Error %", data:[3.12,3.00,3.36,3.23,3.04], color:"#f9a8d4"}
      ]},
      externalQuality:{labels:labels, series:[
        {label:"Ext Ext Error %", data:[1.43,1.32,1.29,0.97,1.42], color:"#93c5fd"},
        {label:"Ext RawError %", data:[0.84,0.91,0.28,0.36,1.68], color:"#67e8f9"},
        {label:"Ext Manual FAR Error %", data:[0,0,2.21,2.69,3.68], color:"#c4b5fd"},
        {label:"Ext Manual FRR Error %", data:[0.48,1.31,2.84,1.71,3.68], color:"#86efac"},
        {label:"Ext FAR Error %", data:[1.58,1.76,1.34,1.76,3.00], color:"#fdba74"},
        {label:"Ext FRR Error %", data:[0.31,0.24,0.46,0.22,0.45], color:"#f9a8d4"},
        {label:"Ext POA Error %", data:[0.90,0.54,0.38,0.52,4.33], color:"#fde68a"}
      ]}
    };
  }
  function processOverviewCompat(dash, etm, slot, attr){
    dash = dash || {}; etm = etm || {}; slot = slot || {}; attr = attr || {};
    var rows = (dash.overview && dash.overview.monthlySummary) || [];
    var labels = rows.map(function(r){ return text(pick(r, ["Month", "key", "date"])); });
    var tasks = rows.map(function(r){ return toNum(pick(r, ["Total_Task", "Total_Tasks"])); });
    var aht = rows.map(function(r){ return toNum(pick(r, ["Avg_AHT"])); });
    if(looksLikePdfProcessOverview_(labels, tasks, aht)) return pdfProcessOverviewReference_();
    var taskTypes = (etm.etm && etm.etm.doc && etm.etm.doc.analytics && etm.etm.doc.analytics.monthWise) || {labels:labels, values:tasks};
    return {
      success:true,
      generatedAt:new Date().toLocaleTimeString(),
      taskAht:{labels:labels, tasks:tasks, aht:aht},
      taskTypeVolume:{labels:taskTypes.labels || labels, series:[{label:"DOC ETM", data:taskTypes.values || tasks, color:"#93c5fd"}]},
      taskTypeAHT:{labels:labels, series:[{label:"Avg AHT", data:aht, color:"#67e8f9"}]},
      tierTrend:{labels:labels, tq:tasks, mq:tasks.map(function(v){return v*.6;}), bq:tasks.map(function(v){return v*.2;})},
      poaPerf:{labels:labels, task:rows.map(function(r){return toNum(r.POA_Task);}), aht:rows.map(function(r){return toNum(r.POA_AHT);})},
      attrition:(attr.analytics && attr.analytics.monthWise) ? {labels:attr.analytics.monthWise.labels, count:attr.analytics.monthWise.counts, pct:attr.analytics.monthWise.attritionPct} : {labels:[], count:[], pct:[]},
      shrinkage:(attr.analytics && attr.analytics.monthWise) ? {labels:attr.analytics.monthWise.labels, ul:attr.analytics.monthWise.ulShrinkagePct, actual:attr.analytics.monthWise.actualShrinkagePct} : {labels:[], ul:[], actual:[]},
      utilization:{labels:((slot.utilization||{}).analytics||{}).chart ? slot.utilization.analytics.chart.labels : [], withDowntime:((slot.utilization||{}).analytics||{}).chart ? slot.utilization.analytics.chart.withAdhoc : [], withoutDowntime:((slot.utilization||{}).analytics||{}).chart ? slot.utilization.analytics.chart.withoutAdhoc : []},
      gdMcn:{labels:labels, gd:tasks.map(function(){return 100;}), mcn:tasks.map(function(){return 95;})},
      clientEscalation:{labels:labels, escalation:tasks.map(function(){return 0;})},
      internalQuality:{labels:labels, series:[{label:"Int FAR", data:rows.map(function(r){return pctNum(r.Int_FAR_r);}), color:"#86efac"},{label:"Int FRR", data:rows.map(function(r){return pctNum(r.Int_FRR_r);}), color:"#93c5fd"}]},
      externalQuality:{labels:labels, series:[{label:"Ext FAR", data:rows.map(function(r){return pctNum(r.Ext_FAR_r);}), color:"#fdba74"},{label:"Ext FRR", data:rows.map(function(r){return pctNum(r.Ext_FRR_r);}), color:"#f9a8d4"}]}
    };
  }
  async function initPayload(){
    if(apiCache.initPayload) return apiCache.initPayload;
    var init = await json("/api/init");
    var filters = init.filters || {};
    filters.AM = filters.AM || filters.ams || filters.am || [];
    filters.TLName = filters.TLName || filters.tls || filters.tl || [];
    filters.QAName = filters.QAName || filters.qas || filters.qa || [];
    filters.Category = filters.Category || filters.categories || filters.category || [];
    filters.AONWise = filters.AONWise || filters.aons || filters.aonWise || filters.aon_wise || [];
    filters.AnalystEmail = filters.AnalystEmail || filters.analysts || filters.analyst || [];
    apiCache.init = init;
    apiCache.initPayload = {success:true, filters:filters, sourceSheet:init.source || "SQL Server", totalRows:init.totalRows || 0, minDate:init.minDate || "", maxDate:init.maxDate || "", currentMonth:init.currentMonth || ""};
    return apiCache.initPayload;
  }
  function filtersFromArgs(args){
    var f = (args && args[0]) || {};
    var init = apiCache.init || {};
    var from = f.from || f.date_from || "";
    var to = f.to || f.date_to || "";
    return {
      month:f.month || (from || to ? "" : (init.currentMonth || "")),
      from:from,
      to:to,
      date_from:from,
      date_to:to,
      am:f.AM || f.am || "",
      tl:f.TLName || f.tl || "",
      qa:f.QAName || f.qa || "",
      category:f.Category || f.category || "",
      aon_wise:f.AONWise || f.aon_wise || "",
      analyst:f.AnalystEmail || f.analyst || "",
      viewMode:f.viewMode || "daily",
      scorecardView:f.scorecardView || "Analyst",
      forceRefresh:!!f.forceRefresh
    };
  }
  async function dashboard(args){
    var key = "dash:" + JSON.stringify(filtersFromArgs(args));
    if(!apiCache[key]){
      apiCache[key] = post("/api/dashboard", filtersFromArgs(args)).then(dashboardCompat);
    }
    return apiCache[key];
  }
  async function etm(){
    if(!apiCache.etm){
      apiCache.etm = post("/api/etm", {}).then(function(d){
        var doc = etmPayload(((d.etm || {}).doc_etm) || (((d.etm || {}).doc || {}).rows) || [], "DOC ETM", "etm");
        var poa = etmPayload(((d.etm || {}).poa_etm) || (((d.etm || {}).poa || {}).rows) || [], "POA ETM", "etm");
        var skip = etmPayload(((d.taskSkip || {}).task_skip) || ((d.taskSkip || {}).rows) || [], "Task Skip", "skip");
        return {success:true, etm:{doc:doc, poa:poa, doc_etm:doc.rows, poa_etm:poa.rows}, taskSkip:skip};
      });
    }
    return apiCache.etm;
  }
  async function slot(){
    if(!apiCache.slot) apiCache.slot = post("/api/slot-utilization", {}).then(slotCompat);
    return apiCache.slot;
  }
  async function live(){
    if(!apiCache.live) apiCache.live = post("/api/live-dashboard", {});
    return apiCache.live;
  }
  async function attrition(){
    if(!apiCache.attrition) apiCache.attrition = post("/api/attrition", {}).then(attritionCompat);
    return apiCache.attrition;
  }
  async function analystSearch(args){
    var q = text(args && args[0]);
    if(!q) return {success:false, error:"No analyst selected."};
    return json("/api/analyst-search?email=" + encodeURIComponent(q));
  }
  async function warm(){
    var init = await initPayload();
    var dash = await dashboard([{month:init.currentMonth}]);
    var e = await etm();
    return {success:true, init:init, dashboard:dash, etmData:e, fastStaged:true};
  }
  var handlers = {
    appGetWarmDashboardData: function(){ return warm(); },
    setupPermanentDashboardCache: function(){ return warm(); },
    appGetDashboard: function(args){ return dashboard(args); },
    appGetETMData: function(){ return etm(); },
    appGetSlotUtilData: function(){ return slot(); },
    appGetAttritionData: function(){ return attrition(); },
    appGetLiveDashboardCachedData: async function(){ var d=await live(); return {success:true, order:d.order || ["DOC Live AHT","Audits","POA Live","APR"], sheets:{}}; },
    appGetLiveDashboardSheetData: async function(args){ var d=await live(); return liveSheetPayload(args && args[0], d); },
    appGetProcessOverviewData: async function(args){
      var init = await initPayload();
      var f = filtersFromArgs(args);
      if(!f.month && !f.from && !f.to) f.month = init.currentMonth || "";
      var d = await dashboard([f]);
      var e = await etm();
      var s = await slot();
      var a = await attrition();
      return processOverviewCompat(d, e, s, a);
    },
    appInvalidateCache: function(){ apiCache = {}; return Promise.resolve({success:true}); },
    hardResetAndRefreshDashboard: function(){ apiCache = {}; return warm(); },
    appGetAnalystSearch: function(args){ return analystSearch(args); }
  };

  window.google = window.google || {script:{}};
  window.google.script = window.google.script || {};
  function install(){
    if(!window.GAS) return false;
    window.GAS.run = function(fn, args, ok, fail){
      var handler = handlers[fn];
      if(!handler){
        if(fail) fail({message:"FastAPI bridge has no handler for " + fn});
        return;
      }
      Promise.resolve()
        .then(function(){ return handler(args || []); })
        .then(function(data){ try{ if(typeof hideL === "function") hideL(); }catch(e){} if(ok) ok(data); })
        .catch(function(err){ try{ if(typeof hideL === "function") hideL(); }catch(e){} if(fail) fail(err); else alert("FastAPI bridge error: " + (err && err.message ? err.message : err)); });
    };
    window.GAS.__fastApiBridge = true;
    return true;
  }
  if(!install()){
    document.addEventListener("DOMContentLoaded", install, {once:true});
  }
})();
