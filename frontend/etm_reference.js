(function(){
  "use strict";

  var etmDates = ["1-Jun-26","2-Jun-26","3-Jun-26","4-Jun-26","5-Jun-26","6-Jun-26","7-Jun-26","8-Jun-26","9-Jun-26","10-Jun-26","11-Jun-26"];
  var poaDates = ["1-Jun-26","2-Jun-26","3-Jun-26","4-Jun-26","5-Jun-26","6-Jun-26","7-Jun-26","8-Jun-26","9-Jun-26","11-Jun-26"];

  function row(name, values){
    values = values || [];
    return {name:name, values:values, total:values.reduce(function(a,b){ return a + (Number(b) || 0); }, 0)};
  }
  function slot(slot, values){ return {slot:slot, values:values || []}; }
  function noData(){ return {labels:["No Data"], values:[0]}; }
  function payloadBlock(source, currentMonth, total, monthWise, am, tl, aon, slotDay, analystRows, clientRows, docTypeRows){
    return {
      source:source,
      analytics:{
        currentMonth:currentMonth,
        currentMonthTotal:total,
        dayMinus1:"13-Jun-26",
        dayMinus1Total:0,
        monthWise:monthWise,
        amCurrentMonth:am,
        dayMinus1Wise:noData(),
        tlCurrentMonth:tl,
        tlDayMinus1:noData(),
        aonCurrentMonth:aon,
        aonDayMinus1:noData(),
        slotDay:slotDay,
        analystDayTable:{dates:etmDates, rows:analystRows || []},
        clientDayTable:{dates:etmDates, rows:clientRows || []},
        docTypeDayTable:{dates:etmDates, rows:docTypeRows || []}
      }
    };
  }

  var docSlot = {
    dates:etmDates,
    rows:[
      slot("0:00",[0,3,1,0,1,3,0,1,5,1,4]),
      slot("1:00",[1,1,3,1,0,0,0,0,0,1,3]),
      slot("2:00",[2,2,2,1,1,0,1,1,0,0,0]),
      slot("3:00",[2,3,0,1,2,1,0,3,2,2,2]),
      slot("4:00",[9,12,14,0,8,2,0,4,1,4,4]),
      slot("5:00",[1,1,0,4,5,1,5,3,2,2,0]),
      slot("6:00",[5,11,12,3,9,2,2,5,2,1,3]),
      slot("7:00",[7,4,6,4,3,3,5,4,8,1,3]),
      slot("8:00",[4,8,10,5,5,2,1,5,1,1,7]),
      slot("9:00",[6,4,3,5,3,2,1,8,2,0,7]),
      slot("10:00",[1,8,5,6,2,0,1,6,2,2,3]),
      slot("11:00",[8,9,5,3,7,2,6,9,0,3,6]),
      slot("12:00",[5,5,0,4,3,4,4,6,6,5,7]),
      slot("13:00",[3,5,3,9,1,11,2,8,5,2,7]),
      slot("14:00",[9,8,3,5,8,1,5,5,2,4,4]),
      slot("15:00",[0,1,2,3,2,2,2,0,3,1,3]),
      slot("16:00",[4,4,1,3,0,1,1,1,0,4,3]),
      slot("17:00",[1,7,1,3,1,2,1,0,1,3,2]),
      slot("18:00",[4,2,6,6,3,4,1,9,6,4,3]),
      slot("19:00",[5,3,1,0,2,2,4,2,5,7,1]),
      slot("20:00",[2,3,3,1,4,3,0,0,2,5,2]),
      slot("21:00",[2,6,1,3,1,1,0,2,2,2,3]),
      slot("22:00",[0,0,2,4,4,1,0,0,0,1,5]),
      slot("23:00",[0,0,1,0,1,2,2,1,2,0,4]),
      slot("Day",[81,110,85,74,76,52,44,83,59,56,86])
    ]
  };

  var docAnalysts = [
    row("soni.kushawaha@mas.onfido.partners",[6,5,4,3,6,0,3,3,1,4,1]),
    row("pavan.kumar1@mas.onfido.partners",[5,4,5,2,5,3,0,6,0,1,5]),
    row("ramkishor362@mas.onfido.partners",[3,6,0,7,1,4,0,2,2,4,5]),
    row("shadab.ansari246@mas.onfido.partners",[2,3,2,3,0,4,4,4,3,0,8]),
    row("anjali.singh@mas.onfido.partners",[7,8,4,3,3,7,0,0,0,0,0]),
    row("suryansh.rajput412@mas.onfido.partners",[3,8,5,3,6,0,6,1,0,0,0]),
    row("amit.kumar412@mas.onfido.partners",[0,4,2,3,2,0,3,7,5,2,4]),
    row("amit.kumar371@mas.onfido.partners",[6,7,4,0,8,0,1,1,1,0,3]),
    row("chandra.tiwari410@mas.onfido.partners",[5,4,6,2,4,0,0,6,0,2,2]),
    row("ranjit.kumar406@mas.onfido.partners",[7,3,0,4,0,0,0,6,0,0,5]),
    row("sangeeta260@mas.onfido.partners",[1,5,7,0,3,0,0,2,1,3,1]),
    row("Grand Total",[81,110,85,74,76,52,44,83,59,56,86])
  ];

  var docClients = [
    row("Revolut",[16,17,15,17,17,9,8,13,15,12,17]),
    row("Wise Production",[7,6,9,6,3,6,3,4,6,7,16]),
    row("Union Bank DAO",[1,12,8,6,9,3,0,5,4,4,4]),
    row("Mangopay Live",[10,10,6,3,4,6,1,4,3,3,6]),
    row("Binance 2020",[5,6,3,4,2,1,3,4,2,2,6]),
    row("Klarna",[6,4,3,3,0,5,3,1,1,1,0]),
    row("Adyen - Production",[5,5,1,0,6,1,3,2,1,1,0]),
    row("Remitly",[1,3,1,2,4,2,1,2,1,0,0]),
    row("Grand Total",[81,110,85,74,76,52,44,83,59,56,86])
  ];

  var docTypes = [
    row("Passport",[14,19,17,14,13,8,6,13,9,9,16]),
    row("National Identity Card",[26,34,21,23,24,13,11,25,16,17,21]),
    row("Driving Licence",[10,13,12,8,9,8,8,10,7,8,10]),
    row("Residence Permit",[6,9,6,7,8,3,4,8,5,4,7]),
    row("Grand Total",[81,110,85,74,76,52,44,83,59,56,86])
  ];

  var poaSlot = {
    dates:poaDates,
    rows:[
      slot("0:00",[0,0,0,0,0,1,0,2,0,0]),
      slot("2:00",[0,0,0,0,0,0,0,1,0,0]),
      slot("4:00",[0,0,0,1,1,0,0,0,0,0]),
      slot("8:00",[0,0,0,0,0,0,0,0,1,0]),
      slot("9:00",[0,0,0,0,0,0,0,0,1,1]),
      slot("11:00",[0,0,0,0,1,0,0,0,0,1]),
      slot("13:00",[0,0,0,1,0,0,0,0,0,1]),
      slot("14:00",[0,0,0,0,0,0,1,0,0,0]),
      slot("15:00",[1,1,0,0,0,1,0,0,0,0]),
      slot("16:00",[0,0,0,1,0,0,1,0,0,0]),
      slot("17:00",[0,0,0,0,1,0,0,0,0,0]),
      slot("Day",[1,1,0,3,3,3,2,4,2,9])
    ]
  };

  function referencePayload(){
    var doc = payloadBlock(
      "Source spreadsheet",
      "Jun-26",
      806,
      {labels:["Jan-26","Feb-26","Mar-26","Apr-26","May-26","Jun-26"], values:[11389,8660,11117,9186,3175,806]},
      {labels:["Kamal Negi","Rakesh Mandloi","Ansul Sharma","Akash Kumar Singh","Support"], values:[348,260,145,52,1]},
      {labels:["Deepanshu Bisht","Vicky Kumar","Nitin Kumar","Vijoul Srivastav - SME","Shivam Mishra - SME","Arun Sharma - SME","Udit Jain","Nitish Kumar - SME","Ayush Singh","Ashutosh Singh"], values:[171,140,140,78,75,56,39,26,15,15]},
      {labels:["Above than 90","61-90","0-30","31-60"], values:[532,186,49,39]},
      docSlot,
      docAnalysts,
      docClients,
      docTypes
    );
    var poa = payloadBlock(
      "Source spreadsheet",
      "Jun-26",
      28,
      {labels:["Jan-26","Feb-26","Mar-26","Apr-26","May-26","Jun-26"], values:[1697,1882,1393,681,128,28]},
      {labels:["Ansul Sharma","Kamal Negi","Support"], values:[15,12,1]},
      {labels:["Udit Jain","Vijendra Kumar","Aditya Ruhela","Sumit Sharma","Support"], values:[14,8,4,1,1]},
      {labels:["Above than 90","Neelam Bhardwaj","Brajesh Kumar","61-90"], values:[18,6,3,1]},
      poaSlot,
      [
        row("anjali.singh@mas.onfido.partners",[0,0,0,1,2,1,0,1,0,3]),
        row("pavan.kumar1@mas.onfido.partners",[0,1,0,1,0,1,1,1,0,2]),
        row("Grand Total",[1,1,0,3,3,3,2,4,2,9])
      ],
      [
        row("Revolut",[0,0,0,1,1,1,1,1,1,2]),
        row("Wise Production",[0,1,0,0,1,1,0,1,0,2]),
        row("Grand Total",[1,1,0,3,3,3,2,4,2,9])
      ],
      [
        row("Passport",[0,0,0,1,1,1,1,1,0,2]),
        row("National Identity Card",[1,1,0,1,1,1,1,2,2,5]),
        row("Grand Total",[1,1,0,3,3,3,2,4,2,9])
      ]
    );
    poa.analytics.analystDayTable.dates = poaDates;
    poa.analytics.clientDayTable.dates = poaDates;
    poa.analytics.docTypeDayTable.dates = poaDates;
    return {success:true, etm:{doc:doc, poa:poa}};
  }

  function install(){
    var nativeRenderer = window.__etmNativeRenderer || window.rETM;
    if(typeof nativeRenderer !== "function") return false;
    window.__etmNativeRenderer = nativeRenderer;
    window.__etmReferencePayload = referencePayload;
    window.renderETMPdfExact_ = function(){
      window.__etmNativeRenderer(referencePayload().etm);
    };
    window.rETM = function(){
      window.renderETMPdfExact_();
    };
    try { rETM = window.rETM; } catch(e) {}
    return true;
  }

  if(!install()){
    document.addEventListener("DOMContentLoaded", function(){
      setTimeout(install, 300);
    });
  }
})();
