function openForm(value, name) {
  //openForm: Completa el formulario con el nombre y precio de compra o venta elejidos por el usuario.
   var type_qoute = document.getElementById("id_type_quote").value;
   document.getElementById("id_name_asset").value = name;
   if (type_qoute == 'sell') {
     document.getElementById("id_previous_quote").value = value.sell;
     localStorage.setItem('buy', value.buy);
     localStorage.setItem('sell', value.sell);
   }
   if (type_qoute == 'buy') {
     document.getElementById("id_previous_quote").value = value.buy;
     localStorage.setItem('buy', value.buy);
     localStorage.setItem('sell', value.sell);
   }
};
function confirm(event) {
  //confirm: evita el envio del formulario y activa los mensajes de confirmacion.
  event.preventDefault();
  mensajes();
};
function mensajes() {
  //messages: Verifica que los datos ingresados por el usuario sean correctos y si lo son activa el envio del formulario.
  var type_umbral = document.getElementById("id_type_umbral").value;
  var value =  document.getElementById("id_previous_quote").value;
  var umbral = document.getElementById("id_umbral").value;
  if (value != "") {
    if (umbral > 0.0) {
       if (type_umbral=="top") {
         if ( parseFloat(umbral) < parseFloat(value)) {
            alert('El umbral introducido no tiene sentido, por que el Valor Actual es "SUPERIOR", introduzca otro valor');
            document.getElementById("id_umbral").value = "";
          }else {
            send();
          }
        } 
        if (type_umbral=="less") {
         if ( parseFloat(umbral) > parseFloat(value)) {
            alert('El umbral introducido no tiene sentido, por que el Valor Actual es "INFERIOR", introduzca otro valor');
            document.getElementById("id_umbral").value = "";
          } else {
            send();
          }
        }
    } else {
      alert('ingrese un numero mayor a 0');
      document.getElementById("id_umbral").value = "";
    }
  } else {
    alert('seleccione un activo');
  }
};
function send() {
  //send: Envia mensajes de exito y envia el formulario.
  alert("La configuracion de alarma ha sido exitosa!!! ");
  alert("Posteriormente, cuando el valor del activo llegue al valor estimado, te lo notificaremos al correo electronico con el que te registraste!!! ");
  document.getElementById("id_name_asset").disabled = false;
  document.getElementById("id_previous_quote").disabled = false;
  document.getElementById("alarmForm").submit();
  };
