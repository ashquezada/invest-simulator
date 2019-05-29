function openForm(value, name , price, id) {
  //openForm: Abre el formulario, guarda los valores pedidos y bloquea el fondo.
  localStorage.setItem('value', JSON.stringify(value));
  localStorage.setItem('name', name);
  localStorage.setItem('price', price);
  localStorage.setItem('id', id);
  document.getElementById("myPopup").style.display = "block";
  document.getElementById("prices").style['pointer-events'] = 'none';
  $("#back").addClass('disable_background');
  put_values_on_the_form();
};
function enableDiv() {
  //enableDiv: Comprueba si se muestra o no el popup.
  if (document.getElementById("myPopup").style.display == "block") {
    on_click_or_keyup();
  } else {
    openForm(JSON.parse(localStorage.value), localStorage.name, localStorage.price);
  }
};
function on_click_or_keyup() {
    //on_click_or_keyup: Comprueba si se dio click en el fondo o se preciono la tecla Esc.
    $("#back0").click(function() {
      closePop();
    });
    $(document).keyup(function(e){
        if(e.which==27) {
           closePop();
        }
    });
};
function closePop(){
  //closePop: Cierra el popup y habilita el fondo.
  document.getElementById("myPopup").style.display = "none";
  document.getElementById("prices").style['pointer-events'] = 'auto';
  $("#back").removeClass('disable_background');
  enable_form();
};
function enable_form()
  //enable_form:funcion vacia necesaria para el correcto funcionamiento de closePop, esta funcion se redefinira en buy.js.
{};
