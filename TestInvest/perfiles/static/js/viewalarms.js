  function send_low_form() {
    //send_low_form: Completa y envia el formulario para dar de baja la alarma.
    document.getElementById("id_id").value = localStorage.id;
    alert("Su alarma a sido dada de baja");
    document.getElementById("my_form").submit();
  };
