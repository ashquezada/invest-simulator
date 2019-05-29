function name_enable(event) {
  //name_enamble: Comprueba que los datos ingresados sean validos.
  event.preventDefault();
  var d = new Date();
  var y = d.getFullYear();
  var m = d.getMonth() + 1;
  var d = d.getDate();
  var date = y + "-" + m + "-" + d 
  since = document.getElementById("id_since").value ;
  until = document.getElementById("id_until").value ;
  if(until > date || since > until ) {
    alert("Error fechas ingresadas invalidas");
    document.getElementById("id_since").value = "" ;
    document.getElementById("id_until").value = "" ;
    document.getElementById("id_time_since").value = "" ;
    document.getElementById("id_time_until").value = "" ;
  } else {
    document.getElementById("id_name").disabled = false;
    document.getElementById("assets_history_form").submit();
  }
};
