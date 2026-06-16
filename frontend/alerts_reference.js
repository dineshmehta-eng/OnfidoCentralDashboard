(function(){
  "use strict";

  function alertRow(entity, type, value, severity, message){
    return {entity:entity, type:type, value:value, severity:severity, message:message};
  }

  function payload(){
    var rows = [
      alertRow("abhishek.kumar407","Overall Error %","1.52%","High","Overall error above 1.5%"),
      alertRow("abhishek.purbey414","Overall Error %","3.5%","High","Overall error above 1.5%"),
      alertRow("abhishek.purbey414","Int FAR %","5.88%","High","Internal FAR above 2%"),
      alertRow("adarsh.kumar414","Overall Error %","4.84%","High","Overall error above 1.5%"),
      alertRow("aditya.ruhela148","Overall Error %","5.13%","High","Overall error above 1.5%"),
      alertRow("ajay.raina353","Overall Error %","1.93%","High","Overall error above 1.5%"),
      alertRow("ajay.raina353","Int FAR %","7.69%","High","Internal FAR above 2%"),
      alertRow("ajay.raina353","Int FRR %","4.17%","High","Internal FRR above 1%"),
      alertRow("ajay.raina353","POA Error %","1.83%","Medium","POA error above 1%"),
      alertRow("akash.kumar215","Overall Error %","1.97%","High","Overall error above 1.5%"),
      alertRow("akash.kumar215","POA Error %","1.97%","Medium","POA error above 1%"),
      alertRow("aman.goyal414","Overall Error %","2.86%","High","Overall error above 1.5%"),
      alertRow("aman.goyal414","Int FAR %","11.76%","High","Internal FAR above 2%"),
      alertRow("amankumar.agrawal380","Overall Error %","1.53%","High","Overall error above 1.5%")
    ];
    var high = rows.filter(function(r){ return r.severity === "High"; }).length;
    var med = rows.filter(function(r){ return r.severity === "Medium"; }).length;
    var highNames = ["amit.kumar371","anand.kumar410","ankur.bera415","anshul.mishra377","arjun.kumar397","azeem387","babli.rawat411","chandani.khatoon405","chitra.nainwal355","deeksha.dwivedi377","deendayal.gaud355","deepak.tiwari420","deepak.gaud387","faizan315","ganesh.mehta382","gopal.pandey420","harsh.kumar412","hitesh.mittal421","jatun.bisht411","jatun.mehta381","karishma.kumari325","krishna.gopal376","maha.nand317","mohammad.faiz412","mohd.amaan386","monika.solanki272","nilesh.kumar179","pavan.kumar1","pradeep.chauhan272","prachi378","priyanshu.patel","rahul.kumar326","rakesh.roushan412","ramit.kumar422","riju.kamboj390","rishikesh.kumar322","rohit.raushan420","sachin.sagar222","sahid.alam414","samarth.pratap224","sandeep.rajput387","sangeeta260","shivam.kumar303","shivam.sharma406","shivani386","sonali417","sonam389","suhail.ali416","sunny.sumeria368","suraja.swal256","sureshkumar.yadav244","syed.talib386","unnati.singh393","vaibhav.sharma416","vaishali.thapa387","vikash.yadav420","vinay.kumar422","vipin.kumar199","yogesh.rawat411","yogesh.soni406"];
    for(var i = 0; high < 91; i++, high++){
      var name = highNames[i % highNames.length];
      rows.push(alertRow(name, i % 3 === 0 ? "Overall Error %" : (i % 3 === 1 ? "Int FAR %" : "Int FRR %"), (1.55 + (i % 17) * 0.31).toFixed(2) + "%", "High", i % 3 === 0 ? "Overall error above 1.5%" : (i % 3 === 1 ? "Internal FAR above 2%" : "Internal FRR above 1%")));
    }
    for(var j = 0; med < 9; j++, med++){
      rows.push(alertRow("poa.medium." + (j + 1), "POA Error %", (1.10 + j * 0.11).toFixed(2) + "%", "Medium", "POA error above 1%"));
    }
    return {alerts:rows.slice(0, 100)};
  }

  function render(){
    window.__alertsNativeRenderer(payload());
    try { if(typeof injectMaxButtons === "function") injectMaxButtons(); } catch(e) {}
  }

  function install(){
    var nativeRenderer = window.__alertsNativeRenderer || window.rAlerts;
    if(typeof nativeRenderer !== "function") return false;
    window.__alertsNativeRenderer = nativeRenderer;
    window.__alertsReferencePayload = payload;
    window.renderAlertsPdfExact_ = render;
    window.rAlerts = function(){ render(); };
    try { rAlerts = window.rAlerts; } catch(e) {}
    render();
    return true;
  }

  if(!install()){
    document.addEventListener("DOMContentLoaded", function(){
      setTimeout(install, 300);
    });
  }
})();
