function comprobar() {
    var cantidad = document.formu.cantidad.value;
    var loc= document.location.href;
    var nombre,cotizacion, devolver;
    var lista = [];
    var getDato;
    var virtual_money = virtual_money;
    if(loc.indexOf('?')>0){
        var getString1 = loc.split("?")[1];
        for (i=0;i<3;i++) {
            getDato = getString1.split("&")[i];
            lista[i] = getDato.split("=")[1];
        }
        if (parseInt(lista[1]) < cantidad) {
            closePop();
            alert("Te pasaste con la cantidad, intente nuevamente.");
            document.getElementById("num").disabled = false;
        } else if (cantidad < 0) {
            closePop();
            alert("Numero negativo no esta permitido, intente nuevamente.");
            document.getElementById("num").disabled = false;
        } else {
            devolver = {
            nombre: lista[0],
            cantidad: cantidad,
            cotizacion: lista[2],
            cant: lista[1],
            }
            return devolver;
        }
    }
}
function Respuesta(v_money) {
    alert("La venta se realizo con exito, Felicidades!!!");
    document.getElementById("id_name").disabled = false;
    document.getElementById("id_total_amount").disabled = false;
    document.getElementById("id_price_sell").disabled = false;
    document.getElementById("id_virtual_money").disabled = false;
    document.getElementById("form").submit();
    closePop();
}
function openForm(v_money) {
    var valor = comprobar();
    var ganancia;
    if(0 < valor.cantidad){
        ganancia =  parseFloat(valor.cantidad)  * parseFloat(valor.cotizacion);
        document.getElementById("myForm").style.display = "block";
        document.getElementById("num").disabled = true;
        document.getElementById("id_name").value = valor.nombre;
        document.getElementById("id_total_amount").value = valor.cantidad;
        document.getElementById("id_total_amount").disabled = true;
        document.getElementById("id_price_sell").value = valor.cotizacion;
        document.getElementById("id_price_sell").disabled = true;
        document.getElementById("id_virtual_money").value = ganancia;
        document.getElementById("id_virtual_money").disabled = true;
        $("#back").addClass('disable_background');
        setTimeout('on_click_or_keyup()',1);
        setTimeout('closePop()',5000);
        return v_money;
    } else {
        closePop();
    }
}
function closePop() {
    $("#back").removeClass('disable_background');
    document.getElementById("myForm").style.display = "none";
    document.getElementById("num").disabled = false;
    document.getElementById("num").value = "";
}
