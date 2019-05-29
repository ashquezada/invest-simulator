  function send() {
    //send: envia formulario para visibilidad.
    document.getElementById("form").submit();
  };
  function mj(event, name, visibility) {
    //mj: Envia mensaje de confirmacion/negacion de visibilidad sobre un activo, bloquea el fondo.
    event.preventDefault();
    document.getElementById("myForm").style.display = 'block';
    $("#back").addClass('disable_background');
    document.getElementById("id_name").value = name;
    document.getElementById("id_visibility").value = visibility;
    if (visibility == 'False') {
      document.getElementById("vis").innerHTML = "La inversión en " + name + " no será visible";
    } else {
    document.getElementById("vis").innerHTML = "La inversión en " + name + " será visible";
    }
  };
