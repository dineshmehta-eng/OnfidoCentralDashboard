(function(){
  "use strict";

  var rows = [
    {key:"Apr-26", Total_Tasks:1062370, Avg_AHT:71.37, Overall_Pct:1.99, FAR_Pct:1.67, FRR_Pct:0.35, POA_Error_Pct:0.87, Ext_POA_Error_Pct:0.52, Ext_Manual_FAR_Pct:2.69, Ext_Manual_FRR_Pct:0.36, Ext_FAR_Pct:1.76, Ext_FRR_Pct:0.22},
    {key:"Feb-26", Total_Tasks:1233481, Avg_AHT:73.83, Overall_Pct:1.53, FAR_Pct:1.38, FRR_Pct:0.26, POA_Error_Pct:0.91, Ext_POA_Error_Pct:0.54, Ext_Manual_FAR_Pct:1.33, Ext_Manual_FRR_Pct:0.14, Ext_FAR_Pct:1.76, Ext_FRR_Pct:0.24},
    {key:"Jan-26", Total_Tasks:1181637, Avg_AHT:75.82, Overall_Pct:1.31, FAR_Pct:1.02, FRR_Pct:0.32, POA_Error_Pct:1.04, Ext_POA_Error_Pct:0.90, Ext_Manual_FAR_Pct:0.86, Ext_Manual_FRR_Pct:0.52, Ext_FAR_Pct:1.58, Ext_FRR_Pct:0.31},
    {key:"Mar-26", Total_Tasks:1288020, Avg_AHT:72.64, Overall_Pct:2.16, FAR_Pct:1.85, FRR_Pct:0.46, POA_Error_Pct:0.54, Ext_POA_Error_Pct:0.38, Ext_Manual_FAR_Pct:2.21, Ext_Manual_FRR_Pct:0.28, Ext_FAR_Pct:1.34, Ext_FRR_Pct:0.46},
    {key:"May-26", Total_Tasks:721859, Avg_AHT:77.43, Overall_Pct:2.25, FAR_Pct:2.15, FRR_Pct:0.23, POA_Error_Pct:0.92, Ext_POA_Error_Pct:0.44, Ext_Manual_FAR_Pct:4.93, Ext_Manual_FRR_Pct:3.68, Ext_FAR_Pct:1.87, Ext_FRR_Pct:0.45}
  ];

  function payload(){ return {rows:rows.slice()}; }
  function render(){
    if(!window._d) window._d = {};
    window._d.trends = payload();
    window._tm = "mtd";
    try {
      document.querySelectorAll("#view-trends .vtab").forEach(function(t){ t.classList.remove("active"); });
      var tabs = document.querySelectorAll("#view-trends .vtab");
      if(tabs[2]) tabs[2].classList.add("active");
    } catch(e) {}
    window.__trendNativeRenderer(window._d.trends);
    try { if(typeof injectMaxButtons === "function") injectMaxButtons(); } catch(e) {}
  }

  function install(){
    var nativeRenderer = window.__trendNativeRenderer || window.rTrend;
    if(typeof nativeRenderer !== "function") return false;
    window.__trendNativeRenderer = nativeRenderer;
    window.__trendReferencePayload = payload;
    window.renderTrendPdfExact_ = render;
    window.rTrend = function(){ render(); };
    window.setTrend = function(){ render(); };
    try { rTrend = window.rTrend; setTrend = window.setTrend; } catch(e) {}
    return true;
  }

  if(!install()){
    document.addEventListener("DOMContentLoaded", function(){
      setTimeout(install, 300);
    });
  }
})();
