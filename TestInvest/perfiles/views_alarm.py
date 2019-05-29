# -- coding: utf-8 --
from __future__ import unicode_literals
from django.shortcuts import render
import json
from .data_api import open_jsons, quit_null_assets
from .models import CustomUser, Alarm
from .forms import AlarmForm, LowAlarmForm
from django.core.mail import EmailMessage, send_mail
import time
from django.template import RequestContext
from datetime import datetime


def send_email(list_alarms):
    """
    send_email: Envía un correo alertando al usuario sobre una alarma
    configurada previamente.
    """
    email_from = 'investsimulatorarg@gmail.com'
    for alarm in list_alarms:
        user = CustomUser.objects.get(pk=alarm[0])
        subject = ("[Invest Simulator] El activo " + str(alarm[1]) +
                   " ha alcanzado el valor esperado")
        body = ("El activo " + str(alarm[1]) +
                " ha alcanzado el valor esperado de " + str(alarm[2]) + ".\n"
                + str(alarm[1]) + "\nValor de cotización previo: " +
                str(alarm[4]) + "\n" + "Valor actual: " + str(alarm[3]) +
                "\nFecha: " + str(datetime.now()))
        send_mail(subject, body, email_from, [user.email], fail_silently=False)


def get_data_of_alarm():
    """ get_data_of_alarm: Chequea si una alarma debe ser disparada o no,
        segun los precios de la API.
    """
    list_alarms = []
    assets = open_jsons()
    assets = quit_null_assets(assets)
    alarms_buy = Alarm.objects.filter(type_quote="buy", type_alarm="high")
    alarms_sell = Alarm.objects.filter(type_quote="sell", type_alarm="high")
    update_alarm_notif(alarms_buy, list_alarms, assets, 'buy')
    update_alarm_notif(alarms_sell, list_alarms, assets, 'sell')
    send_email(list_alarms)


def update_alarm_notif(alarms, list_alarms, assets_json, price):
    """ update_alarm_notif: Chequea que el nombre del activo en la alarma
        coincida con el que brinda en la API.
    """
    for alarm in alarms:
        for nametype, data in assets_json:
            if nametype[1] == alarm.name_asset:
                check_alarms_json(list_alarms, alarm, data, price, nametype)


def check_alarms_json(list_alarms, alarm, data, price, nametype):
    """ check_alarms_json: Compara el precio de la alarma con el precio de
        los activos en la API.
    """
    if alarm.umbral >= data[price] and alarm.type_umbral == "less":
        if not alarm.email_send:
            update_list_alarm(list_alarms, alarm, nametype, data, price)
    elif alarm.type_umbral == "less" and alarm.email_send:
        update_list_alarm(list_alarms, alarm, nametype, data, price)
    if alarm.umbral <= data[price] and alarm.type_umbral == "top":
        if not alarm.email_send:
            update_list_alarm(list_alarms, alarm, nametype, data, price)
    elif alarm.type_umbral == "top" and alarm.email_send:
        update_list_alarm(list_alarms, alarm, nametype, data, price)


def update_list_alarm(list_alarms, alarm, nametype, data, price):
    """ update_list_alarm: Indica si una alarma fue enviada al mail del
        usuario, o se debe enviar.
        [id usuario, nombre activo, umbral, precio actual, precio de creacion]
    """
    if alarm.email_send:
        alarm.email_send = False
    else:
        list_alarms.append([alarm.user_id, nametype[1], alarm.umbral,
                            data[price], alarm.previous_quote])
        alarm.email_send = True
    alarm.save()


def list_alarms(request):
    """ list_alarms: Lista la alarmas creadas por el usuario.
        [nombre activo, tipo umbral, umbral, id alarma, tipo cotizacion]
    """
    alarms = Alarm.objects.filter(user_id=request.user.id, type_alarm="high")
    list_alarms = []
    for alarm in alarms:
        name_asset = alarm.name_asset
        type_umbral = alarm.type_umbral
        umbral = alarm.umbral
        id_alarm = alarm.id
        type_quote = alarm.type_quote
        if type_umbral == "top":
            type_umbral = "Superior"
        elif type_umbral == "less":
            type_umbral = "Inferior"
        if type_quote == "buy":
            type_quote = "Compra"
        elif type_quote == "sell":
            type_quote = "Venta"
        list_alarms.append((name_asset, type_umbral, umbral, id_alarm,
                            type_quote))
    return list_alarms


def low_alarms(request, id_alarm):
    """ low_alarms: Da de baja la alarma deseada del usuario.
    """
    alarms = Alarm.objects.filter(user_id=request.user.id, type_alarm="high")
    for alarm in alarms:
        if id_alarm == alarm.id:
            alarm.type_alarm = "low"
            alarm.save()


def view_alarm(request):
    """ view_alarm: Llena el formulario para dar de baja la alarma deseada del
        usuario.
    """
    pos_ranking = CustomUser.rank_virtualm(request)
    list_alarm = list_alarms(request)
    if request.method == 'POST':
        form_low = LowAlarmForm(request.POST)
        user = request.user.id
        if form_low.is_valid():
            id_low = form_low.cleaned_data.get("id")
            low_alarms(request, id_low)
            list_alarm = list_alarms(request)
        return render(request, 'perfiles/view_alarms.html',
                      {'view_alarms': list_alarm, 'form_low': LowAlarmForm(),
                       'pos_ranking': pos_ranking})
    else:
        form_low = LowAlarmForm()
    return render(request, 'perfiles/view_alarms.html',
                  {'view_alarms': list_alarm, 'form_low': form_low,
                   'pos_ranking': pos_ranking})


def config_alarm(request):
    """ config_alarm: Recibe los datos del formulario para crear la alarma
        deseada.
    """
    pos_ranking = CustomUser.rank_virtualm(request)
    get_data_of_alarm()
    assets = open_jsons()
    assets = quit_null_assets(assets)
    if request.method == 'POST':
        form = AlarmForm(request.POST)
        user = request.user.id
        if form.is_valid():
            type_alarm = form.cleaned_data.get("type_alarm")
            type_quote = form.cleaned_data.get("type_quote")
            type_umbral = form.cleaned_data.get("type_umbral")
            previous_quote = form.cleaned_data.get("previous_quote")
            umbral = form.cleaned_data.get("umbral")
            name_asset = form.cleaned_data.get("name_asset")
            alarm = Alarm.addAlarm(request, type_quote,
                                   type_umbral, umbral, previous_quote,
                                   name_asset)
            list_alarm = list_alarms(request)
        return render(request, 'perfiles/view_alarms.html',
                      {'view_alarms': list_alarm, 'form_low': LowAlarmForm(),
                       'pos_ranking': pos_ranking})
    else:
        form = AlarmForm()
    return render(request, 'perfiles/alarm.html', {
      'assets': assets, 'form': form, 'pos_ranking': pos_ranking})
