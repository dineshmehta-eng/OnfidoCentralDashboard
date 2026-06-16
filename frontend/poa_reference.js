(function(){
  "use strict";

  var months = ["Jan-26", "Feb-26", "Mar-26", "Apr-26", "May-26"];

  function pctRaw(value){
    if(value === null || value === undefined || value === "" || value === "-") return 0;
    return (Number(String(value).replace("%", "")) || 0) / 100;
  }
  function num(value){
    if(value === null || value === undefined || value === "" || value === "-") return 0;
    return Number(String(value).replace(/,/g, "").replace(/s$/i, "")) || 0;
  }
  function monthCell(task, aht, poaErr, extPoa){
    return {
      POA_Task:num(task),
      POA_AHT:num(aht),
      POA_Avg_AHT:num(aht),
      POA_Err_r:pctRaw(poaErr),
      POA_Error_Pct:pctRaw(poaErr),
      Ext_POA_r:pctRaw(extPoa),
      Ext_POA_Error_Pct:pctRaw(extPoa)
    };
  }
  function blankCell(){ return monthCell(0, 0, 0, 0); }
  function entity(name, values){
    var out = {key:name, name:name, months:{}, totalPoaTask:0, POA_Task:0, POA_Avg_AHT:0};
    months.forEach(function(m, i){
      var cell = values[i] ? monthCell(values[i][0], values[i][1], values[i][2], values[i][3]) : blankCell();
      out.months[m] = cell;
      out.totalPoaTask += cell.POA_Task;
      out.POA_Task += cell.POA_Task;
    });
    var weightedAht = 0;
    months.forEach(function(m){
      weightedAht += out.months[m].POA_Task * out.months[m].POA_Avg_AHT;
    });
    out.POA_Avg_AHT = out.POA_Task ? +(weightedAht / out.POA_Task).toFixed(2) : 0;
    out.POA_AHT = out.POA_Avg_AHT;
    return out;
  }
  function d(label, task, aht, aud, err, poaPct, extAud, extErr, extPct){
    return {
      date:label,
      POA_Task:num(task),
      POA_AHT:num(aht),
      POA_Avg_AHT:num(aht),
      POA_Audits_Raw:num(aud),
      POA_Error_Raw:num(err),
      POA_Err_r:pctRaw(poaPct),
      POA_Error_Pct:pctRaw(poaPct),
      Ext_POA_Audits_Raw:num(extAud),
      Ext_POA_Error_Raw:num(extErr),
      Ext_POA_r:pctRaw(extPct),
      Ext_POA_Error_Pct:pctRaw(extPct)
    };
  }

  var amMonth = [
    entity("Kamal Negi", [
      null, [9998, 218.20, "0.60%", "0.18%"], [6839, 213.98, "0.46%", "0.21%"],
      [25925, 203.24, "0.59%", "0.22%"], [36175, 203.06, "0.89%", "0.49%"]
    ]),
    entity("Rakesh Mandloi", [
      [20524, 228.74, "1.11%", "1.22%"], [15171, 217.05, "1.06%", "0.60%"],
      [18474, 222.83, "0.63%", "0.32%"], [6523, 210.60, "0.61%", "0.22%"],
      [150, 187.44, "-", "-"]
    ]),
    entity("Ansul Sharma", [
      null, null, null, [16139, 220.08, "1.09%", "0.81%"], [29228, 214.27, "0.92%", "0.39%"]
    ]),
    entity("Support", [
      [1513, 245.25, "3.57%", "3.08%"], [3545, 260.06, "1.63%", "3.03%"],
      [3648, 261.10, "0.91%", "1.67%"], [3789, 249.73, "2.11%", "1.57%"],
      [3787, 211.95, "1.31%", "0.39%"]
    ]),
    entity("Sachin Ahuja", [null, null, null, null, null]),
    entity("Training", [null, null, null, null, null])
  ];

  var tlMonth = [
    entity("Vijendra Kumar", [
      [20524, 228.74, "1.11%", "1.22%"], null, null,
      [25925, 203.24, "0.59%", "0.22%"], [33490, 202.98, "0.79%", "0.47%"]
    ]),
    entity("Udit Jain", [
      null, [15171, 217.05, "1.06%", "0.60%"], [18474, 222.83, "0.63%", "0.32%"],
      [16139, 220.08, "1.09%", "0.81%"], [29135, 214.26, "0.92%", "0.39%"]
    ]),
    entity("Nitish Kumar - SME", [
      null, [9998, 218.20, "0.60%", "0.18%"], [6839, 213.98, "0.46%", "0.21%"],
      [6523, 210.60, "0.61%", "0.22%"], null
    ]),
    entity("Support", [
      [1513, 245.25, "3.57%", "3.08%"], [3545, 260.06, "1.63%", "3.03%"],
      [3648, 261.10, "0.91%", "1.67%"], [3789, 249.73, "2.11%", "1.57%"],
      [3787, 211.95, "1.31%", "0.39%"]
    ]),
    entity("Aditya Ruhela", [null, null, null, null, [2685, 204.11, "3.55%", "1.37%"]]),
    entity("Arun Sharma - SME", [null, null, null, null, [150, 187.44, "-", "-"]]),
    entity("Sumit Sharma", [null, null, null, null, [92, 218.95, "-", "-"]]),
    entity("Nitin Kumar", [null, null, null, null, [1, 229.00, "-", "-"]])
  ];

  var analystMonth = [
    entity("ajay.raina353", [[2174,229.14,"0.60%","1.83%"],[3025,218.49,"1.10%","-"],[2725,210.39,"0.89%","-"],[2669,221.54,"1.44%","0.61%"],[2663,245.79,"1.83%","-"]]),
    entity("sharukh324", [[2045,212.98,"0.64%","1.42%"],[2379,191.74,"0.67%","2.13%"],[2042,195.95,"0.61%","-"],[1337,198.90,"1.45%","-"],[553,212.43,"0.77%","-"]]),
    entity("shubham.singh133", [null,[1129,194.63,"1.50%","-"],[2023,198.78,"0.22%","0.70%"],[2380,201.31,"0.55%","-"],[2128,206.26,"1.40%","0.65%"]]),
    entity("monu.gangwar141", [null,[998,221.17,"-","-"],[1602,217.32,"-","-"],[2092,214.42,"0.34%","-"],[2263,222.24,"0.52%","-"]]),
    entity("akash.kumar215", [[869,195.71,"1.21%","1.59%"],[766,173.87,"1.78%","3.03%"],[1296,165.04,"1.45%","-"],[1206,161.92,"1.72%","3.08%"],[2046,143.81,"1.97%","0.79%"]]),
    entity("riju.kamboj390", [null,null,[1554,208.92,"-","0.80%"],[2543,207.36,"0.81%","-"],[1927,218.88,"1.30%","0.83%"]]),
    entity("deeksha.dwivedi377", [[1425,283.56,"-","-"],null,[1316,277.02,"0.58%","1.06%"],[1654,258.43,"0.64%","-"],[1583,256.45,"0.40%","-"]]),
    entity("suraja.swal256", [null,null,null,[3034,194.59,"0.29%","-"],[2692,192.61,"0.54%","-"]]),
    entity("priyanshu.patel", [null,null,null,[3223,175.22,"0.59%","0.51%"],[2313,194.44,"0.21%","-"]]),
    entity("sachin.sagar222", [[668,307.61,"0.81%","-"],[852,215.76,"0.71%","-"],[1296,226.57,"-","1.19%"],[756,233.08,"1.43%","1.79%"],[1389,208.68,"1.56%","-"]]),
    entity("dhananjay.tripathi355", [[411,294.62,"-","-"],[828,250.26,"1.08%","-"],[846,260.72,"-","-"],[1032,257.99,"0.44%","-"],[1748,229.70,"-","-"]]),
    entity("faizan315", [[415,263.36,"-","-"],[727,226.51,"-","-"],[801,232.52,"0.72%","-"],[1188,209.82,"0.75%","-"],[1530,211.90,"0.65%","-"]]),
    entity("richa.tariyal286", [null,null,null,[2252,197.59,"0.41%","-"],[2409,182.39,"0.82%","0.56%"]]),
    entity("shivamk.singh387", [null,null,null,[1978,219.29,"1.21%","-"],[2537,220.26,"0.90%","0.67%"]])
  ];

  var dayRows = [
    d("1-May-26",1726,219.71,606,6,"0.99%",86,0,"-"),
    d("2-May-26",1389,222.09,560,2,"0.36%",105,1,"0.95%"),
    d("3-May-26",1356,223.49,603,4,"0.66%",64,0,"-"),
    d("4-May-26",2360,195.18,600,4,"0.67%",289,1,"0.35%"),
    d("5-May-26",2544,201.31,609,4,"0.66%",177,0,"-"),
    d("6-May-26",2895,223.79,599,7,"1.17%",200,0,"-"),
    d("7-May-26",3218,178.76,602,19,"3.16%",305,2,"0.66%"),
    d("8-May-26",2877,190.41,602,1,"0.17%",151,2,"1.32%"),
    d("9-May-26",1431,214.88,901,5,"0.55%",91,0,"-"),
    d("10-May-26",1397,213.32,901,5,"0.55%",105,0,"-"),
    d("11-May-26",3153,205.18,600,16,"2.67%",200,2,"1.00%"),
    d("12-May-26",3132,213.10,300,6,"2.00%",350,2,"0.57%"),
    d("13-May-26",2799,206.27,599,8,"1.34%",200,2,"1.00%"),
    d("14-May-26",2641,229.34,709,4,"0.56%",366,1,"0.27%"),
    d("15-May-26",2605,222.42,751,8,"1.07%",133,1,"0.75%"),
    d("16-May-26",1316,230.22,900,9,"1.00%",76,0,"-"),
    d("17-May-26",1368,220.43,709,5,"0.71%",85,1,"1.18%"),
    d("18-May-26",2747,215.72,576,4,"0.69%",350,1,"0.29%"),
    d("19-May-26",2697,223.84,600,1,"0.17%",350,2,"0.57%"),
    d("20-May-26",2722,210.14,526,2,"0.38%",350,1,"0.29%"),
    d("21-May-26",2610,221.88,583,4,"0.69%",350,0,"-"),
    d("22-May-26",2520,238.58,505,6,"1.19%",150,0,"-"),
    d("23-May-26",1287,260.54,465,6,"1.29%",100,0,"-"),
    d("24-May-26",1124,232.76,529,4,"0.76%",100,2,"2.00%"),
    d("25-May-26",2048,193.37,263,2,"0.76%",0,0,"-"),
    d("26-May-26",2673,190.32,214,0,"-",0,0,"-"),
    d("27-May-26",2677,170.06,237,2,"0.84%",0,0,"-"),
    d("28-May-26",2666,194.72,266,2,"0.75%",0,0,"-"),
    d("29-May-26",2651,170.21,279,1,"0.36%",0,0,"-"),
    d("30-May-26",1303,193.10,202,3,"1.49%",0,0,"-"),
    d("31-May-26",1408,206.37,320,4,"1.25%",0,0,"-")
  ];

  function referencePayload(){
    var base = typeof window.__overviewReferencePayload === "function"
      ? window.__overviewReferencePayload()
      : {};
    var monthly = base.monthlySummary || [];
    return {
      metrics:{
        POA_Task:69340,
        POA_Avg_AHT:208.24,
        POA_AHT:208.24,
        POA_Error_Pct:pctRaw("0.92%"),
        Ext_POA_Error_Pct:pctRaw("0.44%")
      },
      poaMonths:months.slice(),
      byAMMonth:amMonth,
      byTLMonth:tlMonth,
      byAnalystMonth:analystMonth,
      byAM:amMonth,
      byTL:tlMonth,
      byAnalyst:analystMonth,
      monthlySummary:monthly,
      dayTrend:dayRows
    };
  }

  function install(){
    var nativeRenderer = window.__poaNativeRenderer || window.rPoa;
    if(typeof nativeRenderer !== "function") return false;
    window.__poaNativeRenderer = nativeRenderer;
    window.__poaReferencePayload = referencePayload;
    window.renderPoaPdfExact_ = function(){
      var payload = referencePayload();
      window._d = window._d || {};
      window._d.overview = window._d.overview || {};
      if(payload.monthlySummary.length) window._d.overview.monthlySummary = payload.monthlySummary;
      window._d.overview.dayTrend = payload.dayTrend;
      window.__poaNativeRenderer(payload);
    };
    window.rPoa = function(){
      window.renderPoaPdfExact_();
    };
    try { rPoa = window.rPoa; } catch(e) {}
    return true;
  }

  if(!install()){
    document.addEventListener("DOMContentLoaded", function(){
      setTimeout(install, 300);
    });
  }
})();
