(function(){
  "use strict";

  function pctRaw(value){
    if(value === null || value === undefined || value === "" || value === "-") return 0;
    return (Number(String(value).replace("%", "")) || 0) / 100;
  }
  function pctNum(value){
    if(value === null || value === undefined || value === "" || value === "-") return 0;
    return Number(String(value).replace("%", "")) || 0;
  }
  function esc(value){
    return String(value == null ? "" : value).replace(/[&<>"']/g, function(ch){
      return {"&":"&amp;","<":"&lt;",">":"&gt;","\"":"&quot;","'":"&#39;"}[ch];
    });
  }
  function colour(value){
    var v = pctNum(value);
    if(!v) return "var(--muted)";
    if(v >= 1.5) return "var(--red)";
    if(v >= 1.0) return "var(--orange)";
    return "var(--green)";
  }

  var wcHeaders = ["WC 27-Apr-26", "WC 4-May-26", "WC 11-May-26", "WC 18-May-26", "WC 25-May-26"];
  var wcInternal = [
    {label:"Int FAR", values:["2.57%", "2.17%", "1.73%", "2.14%", "3.34%"]},
    {label:"Int FRR", values:["0.28%", "0.24%", "0.34%", "0.25%", "0.19%"]},
    {label:"Int Ext Err", values:["3.72%", "2.56%", "2.42%", "2.27%", "2.55%"]},
    {label:"Int Raw Ext", values:["4.84%", "3.79%", "5.08%", "3.45%", "6.56%"]},
    {label:"Int Add Ext", values:["-", "-", "-", "-", "-"]},
    {label:"Int Classification", values:["2.57%", "2.17%", "1.73%", "2.14%", "3.34%"]},
    {label:"POA Error", values:["0.67%", "0.99%", "1.33%", "0.74%", "0.91%"]}
  ];
  var wcExternal = [
    {label:"Ext FAR", values:["2.93%", "2.44%", "2.56%", "3.16%", "-"]},
    {label:"Ext FRR", values:["0.69%", "1.08%", "0.78%", "0.94%", "-"]},
    {label:"Ext Ext Err", values:["3.18%", "2.47%", "3.35%", "2.25%", "-"]},
    {label:"Ext Add", values:["-", "-", "-", "-", "-"]},
    {label:"Manu FAR", values:["6.67%", "8.12%", "4.73%", "6.58%", "2.48%"]},
    {label:"Manu FRR", values:["33.33%", "8.21%", "2.75%", "2.14%", "1.97%"]},
    {label:"Ext POA %", values:["0.95%", "0.78%", "0.80%", "0.79%", "-"]}
  ];

  function renderTrendTable(hdTrId, tbId, headers, rows){
    var hd = document.getElementById(hdTrId);
    var tb = document.getElementById(tbId);
    if(!hd || !tb) return;
    hd.innerHTML = '<th style="text-align:left;min-width:120px">Metric</th>' +
      headers.map(function(h){ return '<th style="min-width:82px">' + esc(h) + '</th>'; }).join("");
    tb.innerHTML = rows.map(function(row){
      return '<tr><td style="text-align:left;font-weight:600;color:var(--text)">' + esc(row.label) + '</td>' +
        row.values.map(function(value){
          var display = value === "-" ? "&ndash;" : esc(value);
          return '<td style="color:' + colour(value) + ';font-weight:700">' + display + '</td>';
        }).join("") + '</tr>';
    }).join("");
  }

  function patchWeekTables(){
    renderTrendTable("ql-wc-int-hd", "ql-wc-int", wcHeaders, wcInternal);
    renderTrendTable("ql-wc-ext-hd", "ql-wc-ext", wcHeaders, wcExternal);
  }

  function qualityPayload(){
    var base = typeof window.__overviewReferencePayload === "function"
      ? window.__overviewReferencePayload()
      : {};
    return {
      metrics:{
        Overall_Error_Pct:pctRaw("2.25%"),
        Int_FAR_Pct:pctRaw("2.15%"),
        Int_FRR_Pct:pctRaw("0.23%"),
        Ext_Pct:pctRaw("2.43%"),
        Raw_Ext_Pct:pctRaw("4.14%"),
        Ext_FAR_Pct:pctRaw("1.87%"),
        Ext_FRR_Pct:pctRaw("0.45%"),
        Ext_Error_Pct:pctRaw("2.45%"),
        CDQ_Pct:pctRaw("1.81%"),
        Ext_IQ_Pct:0,
        Class_Pct:pctRaw("0.50%"),
        POA_Error_Pct:pctRaw("0.92%"),
        Ext_POA_Error_Pct:pctRaw("0.44%")
      },
      monthly:base.monthlySummary || [],
      dayTrend:base.dayTrend || [],
      tlRows:base.tlRows || [],
      amRows:base.amRows || [],
      aonRows:base.aonRows || [],
      anaRows:base.anaRows || []
    };
  }

  function install(){
    var nativeRenderer = window.__qualityNativeRenderer || window.rQl;
    if(typeof nativeRenderer !== "function") return false;
    window.__qualityNativeRenderer = nativeRenderer;
    window.__qualityReferencePayload = qualityPayload;
    window.renderQualityPdfExact_ = function(){
      window.__qualityNativeRenderer(qualityPayload());
      patchWeekTables();
    };
    window.rQl = function(){
      window.renderQualityPdfExact_();
    };
    try { rQl = window.rQl; } catch(e) {}
    return true;
  }

  if(!install()){
    document.addEventListener("DOMContentLoaded", function(){
      setTimeout(install, 300);
    });
  }
})();
