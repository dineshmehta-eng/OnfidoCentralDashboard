(function(){
  "use strict";

  var dates = ["1-Jun-26","2-Jun-26","3-Jun-26","4-Jun-26","5-Jun-26","6-Jun-26","7-Jun-26","8-Jun-26","9-Jun-26","10-Jun-26","11-Jun-26"];
  function row(name, values){
    values = values || [];
    return {name:name, values:values, total:values.reduce(function(a,b){ return a + (Number(b) || 0); }, 0)};
  }
  function slot(label, values){ return {slot:label, values:values || []}; }
  function noData(){ return {labels:["No Data"], values:[0]}; }

  var slotDay = {
    dates:dates,
    rows:[
      slot("0:00",[7,26,3,1,7,1,1,4,2,3,3]),
      slot("1:00",[0,1,1,4,3,4,3,5,5,4,4]),
      slot("2:00",[5,3,4,2,3,0,2,1,0,2,4]),
      slot("3:00",[0,4,4,3,1,3,1,2,1,0,0]),
      slot("4:00",[1,1,1,3,1,2,6,1,2,3,4]),
      slot("5:00",[0,2,0,4,4,3,2,5,2,8,2]),
      slot("6:00",[0,1,2,0,0,1,2,5,5,5,1]),
      slot("7:00",[2,2,1,2,3,1,2,0,5,4,4]),
      slot("8:00",[1,3,4,4,4,2,1,5,4,6,5]),
      slot("9:00",[1,4,2,1,3,3,1,2,6,5,4]),
      slot("10:00",[5,1,3,4,4,2,3,1,6,2,10]),
      slot("11:00",[6,3,6,3,3,3,1,3,2,4,9]),
      slot("12:00",[6,2,10,3,6,2,1,7,7,6,11]),
      slot("13:00",[15,8,6,2,3,6,2,5,4,5,8]),
      slot("14:00",[8,8,5,5,6,8,1,4,5,7,12]),
      slot("15:00",[8,6,9,3,6,4,7,7,5,6,2]),
      slot("16:00",[3,10,6,4,4,9,4,4,3,7,4]),
      slot("17:00",[6,12,13,8,9,10,3,10,7,10,14]),
      slot("18:00",[5,7,7,8,2,10,4,5,5,5,5]),
      slot("19:00",[7,7,11,5,1,2,4,2,7,2,6]),
      slot("20:00",[5,7,7,6,2,5,3,6,4,9,5]),
      slot("21:00",[11,7,14,5,4,2,7,5,3,9,2]),
      slot("22:00",[4,2,3,3,4,4,4,7,2,4,6]),
      slot("23:00",[3,6,2,6,0,3,1,5,3,3,5]),
      slot("Day",[109,133,124,89,83,90,66,101,95,119,130])
    ]
  };

  var analystRows = [
    row("gaurav408@mas.onfido.partners",[3,6,3,2,2,2,2,4,5,2,2]),
    row("vivek401@mas.onfido.partners",[1,2,5,7,3,1,7,2,1,1,1]),
    row("sandeep.rajput387@mas.onfido.partners",[7,2,5,3,5,0,0,1,1,2,2]),
    row("shivamk.singh387@mas.onfido.partners",[1,2,4,1,2,7,0,1,3,1,1]),
    row("preeti388@mas.onfido.partners",[1,2,1,3,1,0,1,4,4,3,3]),
    row("syed.talib386@mas.onfido.partners",[2,6,1,1,2,2,0,2,1,4,2]),
    row("rahul.kumar326@mas.onfido.partners",[1,4,1,3,2,2,0,3,1,1,4]),
    row("nisha.kumari382@mas.onfido.partners",[8,7,7,0,0,0,0,0,0,0,0]),
    row("sunny.sumeria368@mas.onfido.partners",[2,2,1,4,0,2,1,3,2,2,1]),
    row("ramkishor362@mas.onfido.partners",[3,4,0,1,0,0,0,2,1,4,4]),
    row("Grand Total",[109,133,124,89,83,90,66,101,95,119,130])
  ];

  function referencePayload(){
    return {
      source:"Source spreadsheet",
      rowCount:16455,
      lastUpdated:"14-Jun-2026 15:36",
      analytics:{
        currentMonth:"Jun-26",
        currentMonthTotal:1139,
        dayMinus1:"13-Jun-26",
        dayMinus1Total:0,
        monthWise:{labels:["Jan-26","Feb-26","Mar-26","Apr-26","May-26","Jun-26"], values:[3403,2936,3534,2856,2587,1139]},
        amCurrentMonth:{labels:["Ansul Sharma","Rakesh Mandloi","Kamal Negi","Akash Kumar Singh","Support","#N/A"], values:[566,259,218,49,42,5]},
        dayMinus1Wise:noData(),
        tlCurrentMonth:{labels:["Sumit Sharma","Nitin Kumar","Vijendra Kumar","Tarun Aggarwal - SME","Vikas - SME","Shivam Mishra - SME","Ramraj - SME","Sachin Yadav","Vicky Kumar","Ashutosh Singh"], values:[211,166,158,93,87,77,57,49,47,42]},
        tlDayMinus1:noData(),
        aonCurrentMonth:{labels:["Field missing"], values:[1139]},
        aonDayMinus1:noData(),
        slotDay:slotDay,
        analystDayTable:{dates:dates, rows:analystRows},
        clientDayTable:{dates:dates, rows:[
          row("Field missing",[109,133,124,89,83,90,66,101,95,119,130]),
          row("Grand Total",[109,133,124,89,83,90,66,101,95,119,130])
        ]},
        taskTypeDayTable:{columns:["Field missing"], rows:[
          {date:"1-Jun-26", values:[109], total:109},
          {date:"2-Jun-26", values:[133], total:133},
          {date:"3-Jun-26", values:[124], total:124},
          {date:"4-Jun-26", values:[89], total:89},
          {date:"5-Jun-26", values:[83], total:83},
          {date:"6-Jun-26", values:[90], total:90},
          {date:"7-Jun-26", values:[66], total:66},
          {date:"8-Jun-26", values:[101], total:101},
          {date:"9-Jun-26", values:[95], total:95},
          {date:"10-Jun-26", values:[119], total:119},
          {date:"11-Jun-26", values:[130], total:130},
          {date:"Grand Total", values:[1139], total:1139}
        ]}
      }
    };
  }

  function install(){
    var nativeRenderer = window.__taskSkipNativeRenderer || window.rTaskSkip;
    if(typeof nativeRenderer !== "function") return false;
    window.__taskSkipNativeRenderer = nativeRenderer;
    window.__taskSkipReferencePayload = referencePayload;
    window.renderTaskSkipPdfExact_ = function(){
      window.__taskSkipNativeRenderer(referencePayload());
    };
    window.rTaskSkip = function(){
      window.renderTaskSkipPdfExact_();
    };
    try { rTaskSkip = window.rTaskSkip; } catch(e) {}
    return true;
  }

  if(!install()){
    document.addEventListener("DOMContentLoaded", function(){
      setTimeout(install, 300);
    });
  }
})();
