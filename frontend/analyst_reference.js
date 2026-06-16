(function(){
  "use strict";

  var monthly = [
    {month:"Jan-26", "TOTAL TASK":2563, "AVG AHT":94.69, "POA TASK":0, "POA AVG AHT":0, "POA ERR%":"0%", "EXT POA%":"0%", CRE:"", CRQ:"", "INT EXT%":"0%", "EXT EXT%":"0%", "INT RAW%":"3.33%", "EXT RAW%":"0%", "INT FAR%":"0%", "EXT FAR%":"0%", "INT FRR%":"0%", "EXT FRR%":"0%", "EXT MANUAL FAR%":"0%", "EXT MANUAL FRR%":"0%"},
    {month:"Feb-26", "TOTAL TASK":2173, "AVG AHT":98.48, "POA TASK":0, "POA AVG AHT":0, "POA ERR%":"0%", "EXT POA%":"0%", CRE:"", CRQ:"", "INT EXT%":"0.81%", "EXT EXT%":"0%", "INT RAW%":"0%", "EXT RAW%":"0%", "INT FAR%":"0%", "EXT FAR%":"0%", "INT FRR%":"0%", "EXT FRR%":"0%", "EXT MANUAL FAR%":"0%", "EXT MANUAL FRR%":"0%"},
    {month:"Mar-26", "TOTAL TASK":3379, "AVG AHT":99.21, "POA TASK":0, "POA AVG AHT":0, "POA ERR%":"0%", "EXT POA%":"0%", CRE:"", CRQ:1, "INT EXT%":"2.06%", "EXT EXT%":"0%", "INT RAW%":"0%", "EXT RAW%":"0%", "INT FAR%":"0%", "EXT FAR%":"0%", "INT FRR%":"0%", "EXT FRR%":"0%", "EXT MANUAL FAR%":"0%", "EXT MANUAL FRR%":"0%"},
    {month:"Apr-26", "TOTAL TASK":2089, "AVG AHT":86.25, "POA TASK":200, "POA AVG AHT":169.37, "POA ERR%":"0%", "EXT POA%":"0%", CRE:"", CRQ:"", "INT EXT%":"1.39%", "EXT EXT%":"0%", "INT RAW%":"0%", "EXT RAW%":"0%", "INT FAR%":"0%", "EXT FAR%":"0%", "INT FRR%":"0%", "EXT FRR%":"0%", "EXT MANUAL FAR%":"0%", "EXT MANUAL FRR%":"0%"},
    {month:"May-26", "TOTAL TASK":315, "AVG AHT":88.50, "POA TASK":1598, "POA AVG AHT":144.44, "POA ERR%":"1.58%", "EXT POA%":"0.9%", CRE:"", CRQ:1, "INT EXT%":"0%", "EXT EXT%":"0%", "INT RAW%":"0%", "EXT RAW%":"0%", "INT FAR%":"0%", "EXT FAR%":"0%", "INT FRR%":"0%", "EXT FRR%":"0%", "EXT MANUAL FAR%":"0%", "EXT MANUAL FRR%":"0%"}
  ];

  var attendance = [
    {month:"Jan-26", P:26, HD:0, Leave:1, UL:0},
    {month:"Feb-26", P:17, HD:0, Leave:9, UL:0},
    {month:"Mar-26", P:26, HD:0, Leave:0, UL:0},
    {month:"Apr-26", P:25, HD:0, Leave:1, UL:0},
    {month:"May-26", P:24, HD:0, Leave:2, UL:0}
  ];

  var peerNames = [
    "akash.kumar215","sachin.sagar222","dhananjay.tripathi355","faizan315",
    "vineet.kumar2","shivam.sharma350","ujjwal.tyagi160","riju.kamboj390",
    "deeksha.dwivedi377","priti.pullar386","ajay.raina353","pawan.singh188",
    "shubham.singh133","monu.gangwar141","rahul.gaur222","mohit.kumar301",
    "nilesh.kumar179"
  ];

  function fmtInt(v){
    return (Number(v)||0).toLocaleString("en-IN");
  }
  function fmt2(v){
    return (Number(v)||0).toFixed(2);
  }
  function esc(v){
    return String(v == null ? "" : v).replace(/[&<>"']/g,function(c){
      return {"&":"&amp;","<":"&lt;",">":"&gt;","\"":"&quot;","'":"&#39;"}[c];
    });
  }
  function destroyChart(id){
    try {
      if(window._ch && window._ch[id]){
        window._ch[id].destroy();
        delete window._ch[id];
      }
    } catch(e) {}
  }
  function payload(){
    return {
      success:true,
      name:"sonu.bhatt",
      email:"sonu.bhatt@onfido.com",
      tl:"Udit Jain",
      am:"Prem Rajput",
      qa:"Neelam Bhardwaj",
      aon:"Above than 90",
      category:"Legacy",
      totalDays:114,
      resolvedBy:"",
      myRank:29,
      peerCount:49,
      attendanceMatchedRows:0,
      metrics:{
        Total_Tasks:10519,
        Avg_AHT:95.06,
        POA_Task:1798,
        POA_Avg_AHT:147.22,
        Overall_Error_Pct:0.0103,
        Int_FAR_Pct:0,
        Int_FRR_Pct:0,
        POA_Error_Pct:0.0136
      },
      monthlyBreakdown:monthly.slice(),
      attendanceMonthly:attendance.slice(),
      attendanceDaily:[],
      peerRanking:peerNames.map(function(name, i){
        return {rank:i+1, name:name, Total_Tasks:"", Overall_Error_Pct:null};
      })
    };
  }

  function setSearchBox(){
    var inp = document.getElementById("si");
    if(inp) inp.value = "SONU BHATT";
    var status = document.getElementById("sst");
    if(status) status.textContent = "Loaded from PDF reference.";
  }

  function setKpis(){
    var el = document.getElementById("p-k");
    if(!el) return;
    var items = [
      {l:"Total Tasks", v:"10,519", c:"var(--blue)"},
      {l:"Avg AHT", v:"95.06s", c:"var(--teal)"},
      {l:"POA Task", v:"1,798", c:"var(--green)"},
      {l:"POA AHT", v:"147.22s", c:"var(--orange)"},
      {l:"Overall Err%", v:"1.03%", c:"var(--red)"},
      {l:"Int FAR%", v:"0.00%", c:"var(--green)"},
      {l:"Int FRR%", v:"0.00%", c:"var(--green)"},
      {l:"POA Err%", v:"1.36%", c:"var(--orange)"}
    ];
    el.innerHTML = items.map(function(k){
      return '<div class="pc" style="--pc:'+k.c+'"><label>'+esc(k.l)+'</label><div class="pv">'+esc(k.v)+'</div></div>';
    }).join("");
  }

  function renderPerformanceChart(){
    var el = document.getElementById("c-pt");
    if(!el || typeof Chart === "undefined") return;
    destroyChart("c-pt");
    window._ch = window._ch || {};
    var hasDL = typeof ChartDataLabels !== "undefined";
    var labels = monthly.map(function(r){ return r.month; });
    var tasks = monthly.map(function(r){ return r["TOTAL TASK"]; });
    var aht = monthly.map(function(r){ return r["AVG AHT"]; });
    window._ch["c-pt"] = new Chart(el, {
      type:"bar",
      plugins:hasDL ? [ChartDataLabels] : [],
      data:{
        labels:labels,
        datasets:[
          {
            type:"bar",
            label:"Total Task",
            data:tasks,
            backgroundColor:"#93c5fd99",
            borderColor:"#93c5fd",
            borderWidth:1,
            borderRadius:7,
            yAxisID:"y",
            datalabels:hasDL ? {
              display:true,
              anchor:"center",
              align:"center",
              color:"#07111f",
              backgroundColor:"rgba(255,255,255,.88)",
              borderRadius:5,
              padding:{top:3,bottom:3,left:6,right:6},
              font:{size:11,weight:"900"},
              formatter:function(v){ return v ? fmtInt(v) : ""; }
            } : {display:false}
          },
          {
            type:"line",
            label:"Avg AHT",
            data:aht,
            borderColor:"#fb7185",
            backgroundColor:"#fb718522",
            borderWidth:3,
            pointRadius:5,
            pointBackgroundColor:"#111827",
            pointBorderColor:"#fb7185",
            pointBorderWidth:3,
            tension:.28,
            yAxisID:"y1",
            datalabels:hasDL ? {
              display:true,
              anchor:"end",
              align:"top",
              offset:8,
              color:"#eaf2ff",
              backgroundColor:"rgba(2,6,23,.82)",
              borderColor:"#fb7185",
              borderWidth:1,
              borderRadius:5,
              padding:{top:3,bottom:3,left:5,right:5},
              font:{size:10,weight:"900"},
              formatter:function(v){ return fmt2(v) + "%"; }
            } : {display:false}
          }
        ]
      },
      options:{
        responsive:true,
        maintainAspectRatio:false,
        interaction:{mode:"index",intersect:false},
        layout:{padding:{top:42,right:34,bottom:18,left:12}},
        plugins:{
          legend:{display:true,position:"bottom",labels:{usePointStyle:true,boxWidth:10,padding:14}},
          tooltip:{callbacks:{label:function(ctx){
            return ctx.dataset.label + ": " + (ctx.dataset.label === "Avg AHT" ? fmt2(ctx.parsed.y) + "%" : fmtInt(ctx.parsed.y));
          }}},
          datalabels:{display:hasDL}
        },
        scales:{
          x:{grid:{display:false},ticks:{autoSkip:false,maxRotation:0}},
          y:{beginAtZero:true,suggestedMax:4000,grace:"12%",ticks:{callback:function(v){ return fmtInt(v); }}},
          y1:{position:"right",beginAtZero:true,min:0,max:120,grid:{drawOnChartArea:false},ticks:{callback:function(v){ return v + "%"; }}}
        }
      }
    });
  }

  function renderAttendanceChart(){
    var el = document.getElementById("c-paht");
    if(!el || typeof Chart === "undefined") return;
    destroyChart("c-paht");
    window._ch = window._ch || {};
    var hasDL = typeof ChartDataLabels !== "undefined";
    var labels = attendance.map(function(r){ return r.month; });
    var status = [
      {key:"P", color:"#86efac"},
      {key:"HD", color:"#93c5fd"},
      {key:"Leave", color:"#fde68a"},
      {key:"UL", color:"#fca5a5"}
    ];
    window._ch["c-paht"] = new Chart(el, {
      type:"bar",
      plugins:hasDL ? [ChartDataLabels] : [],
      data:{
        labels:labels,
        datasets:status.map(function(st){
          return {
            label:st.key,
            data:attendance.map(function(r){ return Number(r[st.key]) || 0; }),
            backgroundColor:st.color + "99",
            borderColor:st.color,
            borderWidth:1,
            borderRadius:5
          };
        })
      },
      options:{
        responsive:true,
        maintainAspectRatio:false,
        layout:{padding:{top:34,right:18}},
        plugins:{
          legend:{display:true,position:"bottom",labels:{usePointStyle:true,boxWidth:10,padding:14}},
          datalabels:hasDL ? {
            display:true,
            anchor:"end",
            align:"end",
            color:"#eaf2ff",
            backgroundColor:"rgba(2,6,23,.76)",
            borderRadius:4,
            padding:{top:2,bottom:2,left:5,right:5},
            font:{size:11,weight:"900"},
            formatter:function(v){ return v ? fmtInt(v) : ""; }
          } : {display:false}
        },
        scales:{
          x:{grid:{display:false},ticks:{autoSkip:false,maxRotation:0}},
          y:{beginAtZero:true,suggestedMax:30,ticks:{precision:0,callback:function(v){ return fmtInt(v); }}}
        }
      }
    });
  }

  function renderPeerRows(){
    var el = document.getElementById("p-peer");
    if(!el) return;
    el.innerHTML = peerNames.map(function(name, i){
      var rank = i + 1;
      var rankLabel = rank === 1 ? "&#129351;" : (rank === 2 ? "&#129352;" : (rank === 3 ? "&#129353;" : String(rank)));
      return '<tr><td style="text-align:center;color:var(--muted)">'+rankLabel+'</td><td style="text-align:right">'+esc(name)+'</td><td></td><td></td></tr>';
    }).join("");
  }

  function afterNative(){
    var meta = document.getElementById("pmeta");
    if(meta) meta.textContent = "TL: Udit Jain | AM: Prem Rajput | QA: Neelam Bhardwaj | AON: Above than 90 | Category: Legacy | Active Days: 114";
    var badge = document.getElementById("pbadge");
    if(badge) badge.innerHTML = "&#127942; Rank 29 of 49 in TL team";
    var status = document.getElementById("sst");
    if(status) status.textContent = "";
    setKpis();
    renderPerformanceChart();
    renderAttendanceChart();
    renderPeerRows();
    try {
      if(typeof injectMaxButtons === "function") injectMaxButtons();
      setTimeout(function(){
        try {
          if(window._ch && window._ch["c-pt"]) window._ch["c-pt"].resize();
          if(window._ch && window._ch["c-paht"]) window._ch["c-paht"].resize();
        } catch(e) {}
      }, 120);
    } catch(e) {}
  }

  function renderReference(){
    setSearchBox();
    var nativeRenderer = window.__analystNativeRenderer || window.rProfile;
    if(typeof nativeRenderer !== "function") return false;
    window.__analystNativeRenderer = nativeRenderer;
    nativeRenderer(payload());
    afterNative();
    return true;
  }

  function install(){
    var nativeRenderer = window.__analystNativeRenderer || window.rProfile;
    if(typeof nativeRenderer !== "function") return false;
    window.__analystNativeRenderer = nativeRenderer;
    window.__analystReferencePayload = payload;
    window.renderAnalystPdfExact_ = renderReference;
    window.rProfile = function(){ renderReference(); };
    window.doSrch = function(){ renderReference(); };
    window._fireSearch = function(){ renderReference(); };
    try { rProfile = window.rProfile; doSrch = window.doSrch; _fireSearch = window._fireSearch; } catch(e) {}

    if(Array.isArray(window._ana) && window._ana.indexOf("sonu.bhatt") < 0) window._ana.unshift("sonu.bhatt");
    setSearchBox();

    var oldSwView = window.swView;
    if(typeof oldSwView === "function" && !oldSwView.__analystReferenceWrapped){
      var wrapped = function(id, el){
        var out = oldSwView.apply(this, arguments);
        if(id === "search"){
          setTimeout(function(){ renderReference(); }, 80);
        }
        return out;
      };
      wrapped.__analystReferenceWrapped = true;
      window.swView = wrapped;
      try { swView = window.swView; } catch(e) {}
    }

    var view = document.getElementById("view-search");
    if(view && view.classList.contains("active")){
      setTimeout(function(){ renderReference(); }, 120);
    }
    return true;
  }

  if(!install()){
    document.addEventListener("DOMContentLoaded", function(){
      setTimeout(install, 250);
    });
  }
})();
