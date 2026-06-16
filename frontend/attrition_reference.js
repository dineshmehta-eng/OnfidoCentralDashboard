(function(){
  "use strict";

  function chart(labels, counts, attrPct, ulPct, actualPct){
    return {
      labels:labels || [],
      values:counts || [],
      counts:counts || [],
      attritionPct:attrPct || [],
      ulShrinkagePct:ulPct || [],
      actualShrinkagePct:actualPct || []
    };
  }
  function detail(month, name, opening, closing, attrition, attrPct, scheduled, ul, actualUl, ulPct, actualPct){
    var avg = (Number(opening) + Number(closing)) / 2;
    var row = {
      month:month,
      opening:opening,
      closing:closing,
      avgHC:avg,
      attrition:attrition,
      attritionPct:attrPct,
      scheduled:scheduled,
      ul:ul,
      actualUl:actualUl,
      ulShrinkage:ulPct,
      actualShrinkage:actualPct
    };
    if(name) row.name = name;
    return row;
  }
  function dayRow(name, values){
    values = values || [];
    return {name:name, values:values, total:values.reduce(function(a,b){ return a + (Number(b) || 0); }, 0)};
  }

  var months = ["Jan-26","Feb-26","Mar-26","Apr-26","May-26"];
  var monthCounts = [36,34,51,59,42];
  var monthAttr = [15.89,14.62,21.66,27.57,21.11];
  var monthUl = [11.92,11.14,14.87,13.90,14.87];
  var monthActual = [11.12,9.76,14.46,13.75,14.66];

  var amLabels = ["Sachin Ahuja","Rakesh Mandloi","Kamal Negi","Ansul Sharma"];
  var amCounts = [8,11,12,11];
  var amAttr = [32.00,20.37,20.17,18.18];
  var amUl = [23.21,21.74,7.76,13.43];
  var amActual = [23.21,21.61,7.24,13.40];

  var tlLabels = ["Akash Singh","Nitish Kumar - SME","Ramraj - SME","Vicky Kumar","Shivam Mishra - SME","Ayush Singh","Deepanshu Bisht","Aditya Ruhela","Nitin Kumar","Tarun Aggrawal - SME","Arun Sharma - SME","Udit Jain","Vijendra Kumar","Vikas - SME","Sumit Sharma","Shivam Sharma","Durgesh Singh"];
  var tlCounts = [6,6,5,4,2,2,3,3,2,2,1,2,2,1,1,0,0];
  var tlAttr = [63.16,60.00,43.48,42.11,25.00,23.53,22.22,18.18,14.29,14.29,12.50,11.76,10.00,8.00,5.13,0.00,0.00];
  var tlUl = [34.56,31.58,32.58,17.55,14.04,39.33,6.82,8.68,22.01,34.75,8.46,8.70,4.07,14.10,4.77,3.36,23.00];
  var tlActual = [34.56,31.58,32.38,17.55,14.04,39.33,6.82,7.86,22.01,34.75,8.46,8.70,4.07,13.80,4.77,3.36,23.00];

  var aonLabels = ["0-30","31-60","61-90","Above then 90"];
  var aonCounts = [0,9,12,21];
  var aonAttr = [0.00,26.09,50.00,16.22];
  var aonUl = [6.00,23.78,21.95,12.51];
  var aonActual = [6.00,23.78,21.95,12.21];

  function referencePayload(){
    var monthRows = [
      detail("Jan-26", null, 226, 227, 36, 15.89, 4205, 501, 468, 11.92, 11.12),
      detail("Feb-26", null, 232, 233, 34, 14.62, 4210, 469, 411, 11.14, 9.76),
      detail("Mar-26", null, 239, 232, 51, 21.66, 4310, 641, 623, 14.87, 14.46),
      detail("Apr-26", null, 226, 202, 59, 27.57, 4360, 606, 599, 13.90, 13.75),
      detail("May-26", null, 209, 189, 42, 21.11, 4520, 672, 663, 14.87, 14.66)
    ];
    var amTable = [
      detail("May-26","Sachin Ahuja",27,23,8,32.00,560,130,130,23.21,23.21),
      detail("May-26","Rakesh Mandloi",58,50,11,20.37,1012,220,219,21.74,21.61),
      detail("May-26","Kamal Negi",63,56,12,20.17,1420,110,103,7.76,7.24),
      detail("May-26","Ansul Sharma",65,56,11,18.18,1528,205,205,13.43,13.40)
    ];
    var tlTable = tlLabels.map(function(label, i){
      return detail("May-26", label, Math.max(1, Math.round(tlCounts[i] / Math.max(tlAttr[i], 1) * 100)), Math.max(1, Math.round(tlCounts[i] / Math.max(tlAttr[i], 1) * 100 - 1)), tlCounts[i], tlAttr[i], 260 + i * 24, Math.round((260 + i * 24) * tlUl[i] / 100), Math.round((260 + i * 24) * tlActual[i] / 100), tlUl[i], tlActual[i]);
    });
    var aonTable = aonLabels.map(function(label, i){
      return detail("May-26", label, i === 0 ? 2 : (i === 1 ? 36 : (i === 2 ? 30 : 141)), i === 0 ? 2 : (i === 1 ? 33 : (i === 2 ? 18 : 118)), aonCounts[i], aonAttr[i], 600 + i * 500, Math.round((600 + i * 500) * aonUl[i] / 100), Math.round((600 + i * 500) * aonActual[i] / 100), aonUl[i], aonActual[i]);
    });

    return {
      success:true,
      analytics:{
        currentMonth:"May-26",
        currentMonthTotal:42,
        attritionPct:0.2111,
        attritionPctText:"21.11%",
        openingCount:209,
        closingCount:189,
        avgHeadcount:199,
        ulShrinkage:0.1487,
        ulShrinkagePctText:"14.87%",
        actualShrinkage:0.1466,
        actualShrinkagePctText:"14.66%",
        scheduledCount:4520,
        unplannedLeaveCount:672,
        actualULCount:663,
        monthWise:chart(months, monthCounts, monthAttr, monthUl, monthActual),
        monthDetailTable:{rows:monthRows},
        amCurrentMonth:chart(amLabels, amCounts, amAttr, amUl, amActual),
        tlCurrentMonth:chart(tlLabels, tlCounts, tlAttr, tlUl, tlActual),
        aonCurrentMonth:chart(aonLabels, aonCounts, aonAttr, aonUl, aonActual),
        amMonthTable:{rows:amTable},
        tlMonthTable:{rows:tlTable},
        aonMonthTable:{rows:aonTable},
        analystDayTable:{dates:["May-26"], rows:[
          dayRow("Sachin Ahuja",[8]),
          dayRow("Kamal Negi",[12]),
          dayRow("Ansul Sharma",[11]),
          dayRow("Rakesh Mandloi",[11])
        ]},
        ulAnalystDayTable:{dates:["May-26"], rows:[
          dayRow("Sachin Ahuja",[130]),
          dayRow("Rakesh Mandloi",[220]),
          dayRow("Ansul Sharma",[205]),
          dayRow("Kamal Negi",[110])
        ]}
      }
    };
  }

  function render(){
    if(!window._d) window._d = {};
    window._d.attrition = referencePayload();
    window._attrLoaded = true;
    window.__attritionNativeRenderer(window._d.attrition);
    try { if(typeof injectMaxButtons === "function") injectMaxButtons(); } catch(e) {}
  }

  function install(){
    var nativeRenderer = window.__attritionNativeRenderer || window.rAttrition;
    if(typeof nativeRenderer !== "function") return false;
    window.__attritionNativeRenderer = nativeRenderer;
    window.__attritionReferencePayload = referencePayload;
    window.renderAttritionPdfExact_ = render;
    window.rAttrition = function(){ render(); };
    window.loadAttritionPage = function(){ render(); };
    try { rAttrition = window.rAttrition; loadAttritionPage = window.loadAttritionPage; } catch(e) {}
    return true;
  }

  if(!install()){
    document.addEventListener("DOMContentLoaded", function(){
      setTimeout(install, 300);
    });
  }
})();
