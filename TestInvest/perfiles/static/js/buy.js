function enviar() {
  //enviar: Arma y muestra mensaje para confirmar la compra.
  document.getElementById("myForm_buy").style.display = "none";
  var amount = document.getElementById("id_total_amount").value;
  var total_amount = localStorage.sell * amount;
  totalTiempo=5;
  buy_confirm = $("#confirm");
  msg = msg_confirm(amount, total_amount);
  buy_confirm.find(".message").text(msg);
  updateReloj();
  buy_confirm.show();
};
function openFormu() {
  //openFormu abre el popup de visibilidad.
  document.getElementById("id_visibility").disabled = true;
  document.getElementById("myForm_buy").style.display = "block";
};
function success() {
  //success: envia formulario de compra.
  alert("La compra se realizo con exito!!");
  document.getElementById("id_total_amount").disabled = false;
  document.getElementById("id_name").disabled = false;
  document.getElementById("id_visibility").disabled = false;
  document.getElementById("buy_form").submit();
};
function enable_form() {
  //enable_form: Habilita el formulario de compra.
  document.getElementById("confirm").style.display = 'none';
  document.getElementById("accept").disabled = false;
  document.getElementById("cancel").disabled = false;
  document.getElementById("id_total_amount").disabled = false;
  document.getElementById("id_total_amount").value = "";
  document.getElementById("id_visibility").disabled = false;
  document.getElementById("total").innerHTML = "Subtotal: $0";
};
function updateReloj() {
  //updateReloj: Actualiza el reloj mostrado en mensaje de confirmacion.
  document.getElementById('time').innerHTML = `${totalTiempo}`;
  var close = $("#confirm");
  if (totalTiempo==0) {
    close.hide();
    enable_form();
    document.getElementById('time').innerHTML = "";
  } else {
      totalTiempo-=1;
      setTimeout("updateReloj()",1000);
  }
};
function msg_confirm(amount, total_amount ) {
  //msg_confirm: Arma mensaje de confirmacion.
  localStorage.setItem('amounts', amount);
  localStorage.setItem('total_amount', total_amount);
  var msg = `Activo adquirido: ${localStorage.name}
  A seleccionado: ${amount}
  Precio compra: ${localStorage.sell},
  Precio venta: ${localStorage.buy}.
  A un total de: ${total_amount}.
  ¿Esta seguro que desea comprar esta cantidad del activo?`
  return msg
};
function confirm(event, virtual_money) {
  //confirm: Comprueba que los datos ingresados por el usuario sean validos.
  event.preventDefault();
  var virtual_money = parseFloat(virtual_money.replace(",", "."));
  document.getElementById("accept").disabled = true;
  document.getElementById("cancel").disabled = true;
  document.getElementById("id_total_amount").disabled = true;
  var amount = document.getElementById("id_total_amount").value;
  var total_amount = localStorage.sell * amount;
  visibility = document.getElementById("id_visibility").value;
  if (amount > 0) {
    if (virtual_money >= total_amount) {
      if (visibility == 'True') {
        openFormu();
      } else {
        totalTiempo=5;
        buy_confirm = $("#confirm");
        msg = msg_confirm(amount, total_amount );
        buy_confirm.find(".message").text(msg);
        updateReloj();
        buy_confirm.show();
      } 
    } else {
      alert("No dispone saldo suficiente para realizar la compra");
      enable_form();
    }
  } else {
    alert("Ingrese un numero valido (mayor a cero)");
    enable_form();
  }
};
