(function(){
  "use strict";

  function chart(labels, values, aht){
    return {labels:labels || [], values:values || [], aht:aht || []};
  }
  function pair(task, aht){ return {task:task || 0, aht:aht || 0}; }
  function poaRow(name, task, aht, b0, b1, b2, b3, supported, unsupported){
    return {name:name, task:task || 0, aht:aht || 0, b0:b0 || 0, b1:b1 || 0, b2:b2 || 0, b3:b3 || 0, supported:supported || 0, unsupported:unsupported || 0};
  }
  function hms(value){
    var parts = String(value || "0:00:00").split(":").map(function(x){ return Number(x) || 0; });
    while(parts.length < 3) parts.unshift(0);
    return parts[0] + parts[1] / 60 + parts[2] / 3600;
  }
  function pct(value){
    if(value === null || value === undefined || value === "" || value === "-") return 0;
    return (Number(String(value).replace("%", "")) || 0) / 100;
  }
  function aprRow(name, netText, values){
    return {name:name, net:hms(netText), netText:netText, values:(values || []).map(pct)};
  }

  var docTypes = ["ADD_EXTRACTION","CLASSIFICATION","CONSISTENCY","EXTRACTION","FRAUD","RAW_EXTRACTION"];
  function docTypeRow(name, values){
    return {name:name, values:values.map(function(v){ return pair(v[0], v[1]); })};
  }

  var docSlotRows = [
    ["0:30",332,83.62,186,94.55,146,69.69],
    ["1:30",272,90.79,157,100.20,115,77.94],
    ["2:30",258,79.81,137,86.14,121,72.64],
    ["3:30",188,80.43,115,83.09,73,76.23],
    ["4:30",166,90.30,110,101.22,56,68.84],
    ["5:30",201,76.31,104,77.42,97,75.11],
    ["6:30",185,80.54,106,87.91,79,70.65],
    ["7:30",117,84.92,74,85.19,43,84.47],
    ["8:30",166,74.23,102,81.72,64,62.30],
    ["9:30",178,69.60,99,76.81,79,60.57],
    ["10:30",136,81.04,89,87.63,47,68.55],
    ["11:30",154,87.27,75,101.11,79,74.13],
    ["12:30",253,78.32,149,83.46,104,70.95],
    ["13:30",313,99.80,166,117.33,147,80.01],
    ["14:30",326,104.84,183,122.04,143,82.83],
    ["15:30",335,95.86,197,107.39,138,79.41],
    ["16:30",289,106.25,193,118.91,96,80.80],
    ["17:30",372,115.92,234,129.89,138,92.22],
    ["18:30",410,106.36,239,121.85,171,84.71],
    ["19:30",396,98.91,202,118.73,194,78.27],
    ["20:30",388,101.96,221,121.65,167,75.90],
    ["21:30",293,114.01,173,138.79,120,78.29],
    ["22:30",275,88.96,131,99.60,144,79.27],
    ["23:30",312,87.79,163,101.23,149,73.09]
  ].map(function(r){
    return {name:r[0], task:r[1], aht:r[2], values:[pair(r[3], r[4]), pair(r[5], r[6])]};
  });

  var poaSlotRows = [
    ["0:30",79,244.04,77,2,0,0,57,22],
    ["1:30",69,180.13,69,0,0,0,42,27],
    ["2:30",50,244.92,50,0,0,0,37,13],
    ["3:30",36,191.61,36,0,0,0,19,17],
    ["4:30",56,175.75,56,0,0,0,27,29],
    ["5:30",34,175.62,34,0,0,0,21,13],
    ["6:30",41,173.59,41,0,0,0,26,15],
    ["7:30",25,149.20,25,0,0,0,11,14],
    ["8:30",32,262.81,31,1,0,0,25,7],
    ["9:30",37,199.62,37,0,0,0,24,13],
    ["10:30",33,205.39,32,1,0,0,24,9],
    ["11:30",53,210.21,51,2,0,0,27,26],
    ["12:30",91,205.34,90,1,0,0,50,41],
    ["13:30",76,221.07,76,0,0,0,42,34],
    ["14:30",90,252.33,89,1,0,0,52,38],
    ["15:30",120,191.34,120,0,0,0,57,63],
    ["16:30",72,210.06,72,0,0,0,45,27],
    ["17:30",101,203.81,101,0,0,0,60,41],
    ["18:30",82,213.56,82,0,0,0,45,37],
    ["19:30",104,224.90,103,1,0,0,53,51],
    ["20:30",99,205.28,99,0,0,0,54,45],
    ["21:30",99,151.04,99,0,0,0,43,56],
    ["22:30",53,263.81,52,1,0,0,40,13],
    ["23:30",64,231.02,64,0,0,0,39,25]
  ].map(function(r){ return poaRow.apply(null, r); });

  function referencePayload(){
    var doc = {
      success:true,
      rowCount:6315,
      fullRowCount:6315,
      liveAnalytics:{
        taskCount:6315,
        avgAHT:93.63,
        amTrend:chart(
          ["Rakesh Mandloi","Ansul Sharma","Kamal Negi","Akash Kumar Singh","Support","Training"],
          [2239,1939,1163,847,89,38],
          [83.39,78.62,89.36,152.47,154.11,139.76]
        ),
        tlTrend:chart(
          ["Nitin Kumar","Tarun Aggarwal - SME","Udit Jain","Deepanshu Bisht","Arun Sharma - SME","Vikas - SME","Ayush Singh","Shivam Mishra - SME","Vijendra Kumar","Nitish Kumar - SME","Sachin Yadav","Ramraj - SME","Vicky Kumar","Support","Akash Kumar Singh","Training"],
          [971,796,619,588,489,391,249,247,237,197,177,166,156,89,53,38],
          [70.49,82.54,85.12,91.54,84.56,86.10,95.17,197.02,133.98,158.52,92.82,105.42,89.35,154.11,111.51,139.76]
        ),
        aonTrend:chart(
          ["Above than 90","0-30","61-90","31-60","Blank"],
          [4142,999,601,535,38],
          [82.92,141.99,86.56,90.93,139.76]
        ),
        slotMatrix:{statusHeaders:["Extraction Only","Legacy"], rows:docSlotRows},
        analystTaskTypeMatrix:{firstHeader:"Analyst Email", types:docTypes, rows:[
          docTypeRow("shadab.ansari246@mas.onfido.partners", [[0,0],[0,0],[0,0],[0,0],[175,65.45],[1,78.00]]),
          docTypeRow("achal.sharma386@mas.onfido.partners", [[0,0],[1,25.00],[0,0],[2,70.00],[154,56.16],[3,174.00]]),
          docTypeRow("sangeeta260@mas.onfido.partners", [[0,0],[1,24.00],[0,0],[0,0],[158,66.01],[0,0]]),
          docTypeRow("mohammad.faiz412@mas.onfido.partners", [[1,11.00],[0,0],[0,0],[6,122.50],[131,59.02],[4,124.00]]),
          docTypeRow("sureshkumar.yadav244@mas.onfido.partners", [[0,0],[0,0],[0,0],[0,0],[135,58.96],[0,0]]),
          docTypeRow("mohd.amaan386@mas.onfido.partners", [[0,0],[0,0],[0,0],[2,104.50],[127,64.43],[1,241.00]])
        ]},
        clientTaskTypeMatrix:{firstHeader:"IMS Client Name", types:docTypes, rows:[
          docTypeRow("Revolut", [[60,69.30],[87,33.99],[4,14.25],[362,130.21],[332,62.88],[287,171.08]]),
          docTypeRow("Wise Production", [[0,0],[75,32.23],[10,20.10],[135,132.46],[132,68.46],[71,165.14]]),
          docTypeRow("Union Bank DAO", [[0,0],[14,16.57],[0,0],[91,44.51],[125,45.97],[132,81.52]]),
          docTypeRow("Binance 2020", [[0,0],[30,25.73],[2,20.50],[162,121.02],[76,58.47],[32,113.16]]),
          docTypeRow("Mangopay Live", [[0,0],[16,32.63],[1,11.00],[20,124.95],[127,71.17],[80,143.19]]),
          docTypeRow("Remitly", [[6,71.00],[34,29.62],[0,0],[58,131.29],[71,59.20],[57,111.05]])
        ]},
        docTaskTypeMatrix:{firstHeader:"Document Type Full Name", types:docTypes, rows:[
          docTypeRow("Blank", [[0,0],[177,33.62],[0,0],[10,91.60],[117,65.32],[197,94.96]]),
          docTypeRow("Philippines National Identity Card", [[0,0],[0,0],[0,0],[0,0],[120,40.70],[168,84.68]]),
          docTypeRow("India Passport", [[45,22.07],[34,18.94],[0,0],[82,81.56],[49,63.78],[4,92.00]]),
          docTypeRow("France National Identity Card", [[0,0],[4,24.00],[1,4.00],[0,0],[96,61.48],[95,169.37]]),
          docTypeRow("Greece National Identity Card", [[0,0],[6,45.00],[0,0],[116,130.22],[36,60.42],[0,0]]),
          docTypeRow("Romania National Identity Card", [[8,185.38],[2,18.00],[1,4.00],[10,186.70],[93,66.89],[35,114.03]])
        ]}
      }
    };

    var poa = {
      success:true,
      rowCount:1596,
      fullRowCount:1596,
      liveAnalytics:{
        taskCount:1596,
        avgAHT:208.67,
        amTrend:chart(
          ["Kamal Negi","Ansul Sharma","Rakesh Mandloi","Support"],
          [762,637,137,60],
          [209.19,203.68,219.34,230.82]
        ),
        tlTrend:chart(
          ["Vijendra Kumar","Udit Jain","Aditya Ruhela","Sumit Sharma","Arun Sharma - SME","Support","Shivam Mishra - SME"],
          [561,512,201,125,92,60,45],
          [199.27,211.10,236.87,173.29,191.02,230.82,277.22]
        ),
        slotMatrix:{rows:poaSlotRows},
        analystMatrix:{rows:[
          poaRow("riju.kamboj390@mas.onfido.partners",90,185.47,90,0,0,0,58,32),
          poaRow("richa.tariyal286@mas.onfido.partners",76,196.13,74,2,0,0,46,30),
          poaRow("sachin.kushwaha387@mas.onfido.partners",71,217.06,71,0,0,0,43,28),
          poaRow("vipin.kumar199@mas.onfido.partners",71,158.59,71,0,0,0,44,27),
          poaRow("priyanshu.singh387@mas.onfido.partners",71,234.89,71,0,0,0,38,33),
          poaRow("mohit.chauhan207@mas.onfido.partners",69,195.86,69,0,0,0,35,34),
          poaRow("suraja.swal256@mas.onfido.partners",67,155.78,67,0,0,0,37,30),
          poaRow("azeem387@mas.onfido.partners",65,191.80,65,0,0,0,37,28),
          poaRow("pawan.singh188@mas.onfido.partners",61,198.56,61,0,0,0,37,24),
          poaRow("shivani.pal250@mas.onfido.partners",60,170.77,60,0,0,0,33,27),
          poaRow("nilesh.kumar179@mas.onfido.partners",56,194.13,56,0,0,0,32,24)
        ]},
        clientMatrix:{rows:[
          poaRow("Coinbase POA - Live",382,218.00,380,2,0,0,232,150),
          poaRow("PWC",317,80.11,317,0,0,0,7,310),
          poaRow("Crypto",247,249.95,244,3,0,0,191,56),
          poaRow("Zinc",101,265.40,100,1,0,0,77,24),
          poaRow("HSBC SmartServe",48,264.77,48,0,0,0,46,2),
          poaRow("Monese QES",38,257.21,38,0,0,0,26,12),
          poaRow("Bybit",37,271.57,37,0,0,0,31,6),
          poaRow("Legal",34,267.62,34,0,0,0,31,3)
        ]}
      }
    };

    var aprSlotRows = [
      aprRow("0:30","58:58:48",["45.71%","54.96%","58.03%","33.38%","11.63%","46.68%","-"]),
      aprRow("1:30","47:55:12",["41.69%","56.82%","40.80%","9.10%","19.73%","54.22%","-"]),
      aprRow("2:30","50:52:48",["37.94%","53.02%","43.97%","16.98%","9.81%","40.46%","-"]),
      aprRow("3:30","47:18:36",["38.05%","68.61%","55.83%","7.68%","24.67%","22.95%","-"]),
      aprRow("4:30","40:30:00",["24.87%","62.21%","35.07%","14.86%","18.81%","64.08%","-"]),
      aprRow("5:30","32:56:24",["17.74%","62.11%","19.26%","15.87%","2.37%","100.00%","-"]),
      aprRow("6:30","35:46:12",["50.27%","73.52%","47.30%","35.57%","14.08%","65.50%","-"]),
      aprRow("7:30","28:21:36",["49.91%","77.73%","65.88%","39.42%","39.68%","-","72.83%"]),
      aprRow("8:30","29:12:36",["43.18%","63.62%","64.41%","22.84%","15.62%","-","84.90%"]),
      aprRow("9:30","31:07:48",["16.75%","71.76%","54.89%","6.32%","7.17%","-","81.59%"]),
      aprRow("10:30","31:55:48",["23.93%","64.15%","33.16%","21.92%","20.14%","-","91.12%"]),
      aprRow("11:30","36:19:12",["34.37%","65.10%","40.14%","27.92%","17.11%","-","86.06%"]),
      aprRow("12:30","43:53:24",["29.62%","51.76%","37.69%","15.56%","4.50%","36.05%","68.25%"]),
      aprRow("13:30","53:00:36",["19.48%","49.21%","32.22%","16.58%","2.11%","-","34.00%"]),
      aprRow("14:30","58:34:12",["20.18%","44.50%","32.99%","17.91%","4.95%","-","-"]),
      aprRow("15:30","63:09:36",["31.26%","52.17%","49.60%","46.77%","7.02%","-","90.97%"]),
      aprRow("16:30","66:09:36",["23.09%","59.23%","50.24%","40.68%","21.98%","-","82.20%"]),
      aprRow("17:30","73:42:00",["25.70%","49.30%","39.46%","28.65%","2.57%","-","74.72%"]),
      aprRow("18:30","70:28:12",["25.04%","59.23%","40.79%","27.73%","-","-","-"]),
      aprRow("19:30","64:50:24",["21.66%","47.58%","34.66%","26.61%","-","-","-"]),
      aprRow("20:30","68:55:48",["18.99%","44.65%","31.87%","17.99%","-","100.00%","-"]),
      aprRow("21:30","73:01:12",["29.68%","60.37%","45.63%","32.32%","28.70%","80.76%","-"]),
      aprRow("22:30","63:13:12",["35.16%","67.50%","53.07%","32.07%","27.61%","48.34%","-"]),
      aprRow("23:30","57:51:36",["35.84%","56.89%","55.30%","37.57%","19.67%","48.64%","-"])
    ];
    var apr = {
      success:true,
      rowCount:0,
      fullRowCount:0,
      liveAnalytics:{
        poaLiveAHT:208.67,
        amTrend:{labels:["Akash Kumar Singh","Ansul Sharma","Rakesh Mandloi","Training","#N/A"], netLogin:[hms("0:25:56"),hms("0:42:36"),hms("0:34:21"),hms("0:30:00"),hms("0:23:26")], netLoginText:["0:25:56","0:42:36","0:34:21","0:30:00","0:23:26"], avail:[32.66,53.83,55.00,54.00,0]},
        tlTrend:{labels:["Shivam Mishra - SME","Deepanshu Bisht","Arun Sharma - SME","Sumit Sharma","Nitish Kumar - SME"], netLogin:[hms("0:25:00"),hms("0:27:15"),hms("0:35:01"),hms("0:41:21"),hms("0:27:23")], netLoginText:["0:25:00","0:27:15","0:35:01","0:41:21","0:27:23"], avail:[31.54,49.59,60.94,54.49,43.55]},
        aonTrend:{labels:["0-30","61-90","Above than 90","31-60","Blank","#N/A"], netLogin:[hms("0:26:00"),hms("0:25:48"),hms("0:25:05"),hms("0:25:17"),hms("0:24:34"),hms("0:19:26")], netLoginText:["0:26:00","0:25:48","0:25:05","0:25:17","0:24:34","0:19:26"], avail:[39.09,39.09,49.86,31.66,43.89,0]},
        slotMatrix:{queues:["Junior Queue","POA Queue","Extraction Only","Senior Queue","Priority Queue","Support","Appen"], rows:aprSlotRows},
        analystMatrix:{queues:["Junior Queue","POA Queue","Extraction Only","Senior Queue","Priority Queue","Support","Appen"], rows:[
          aprRow("sachin.kushwaha387@mas.onfido.partners","27:27:00",["-","82.69%","-","-","-","-","-"])
        ]}
      }
    };

    return {success:true, order:["DOC Live AHT","Audits","POA Live","APR"], sheets:{
      "DOC Live AHT":doc,
      "Audits":{success:true, rowCount:0, fullRowCount:0, liveAnalytics:{todayAuditCount:0, todayErrorCount:0}},
      "POA Live":poa,
      "APR":apr
    }};
  }

  function markStatuses(){
    ["DOC Live AHT","Audits","POA Live","APR"].forEach(function(name){
      try{
        if(typeof setLiveStatus === "function") setLiveStatus(name, "ok", "Loaded", "PDF reference");
      }catch(e){}
    });
  }

  function render(){
    if(!window._d) window._d = {};
    window._d.liveDashboard = referencePayload();
    window._liveLoaded = true;
    markStatuses();
    window.__liveNativeRenderer(window._d.liveDashboard);
    try { if(typeof injectMaxButtons === "function") injectMaxButtons(); } catch(e) {}
  }

  function install(){
    var nativeRenderer = window.__liveNativeRenderer || window.rLiveDashboard;
    if(typeof nativeRenderer !== "function") return false;
    window.__liveNativeRenderer = nativeRenderer;
    window.__liveReferencePayload = referencePayload;
    window.renderLiveDashboardPdfExact_ = render;
    window.rLiveDashboard = function(){ render(); };
    window.loadLiveDashboardPage = function(){ render(); };
    window.forceRefreshLive = function(){ render(); };
    try { rLiveDashboard = window.rLiveDashboard; loadLiveDashboardPage = window.loadLiveDashboardPage; forceRefreshLive = window.forceRefreshLive; } catch(e) {}
    return true;
  }

  if(!install()){
    document.addEventListener("DOMContentLoaded", function(){
      setTimeout(install, 300);
    });
  }
})();
