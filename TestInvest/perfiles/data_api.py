# -- coding: utf-8 --
from __future__ import unicode_literals
import time
from django.template import RequestContext
from datetime import datetime
from django.core.mail import EmailMessage, send_mail
from django.contrib.auth.decorators import login_required
import json


def open_jsons():
    '''
    Lee los archivos .json y devuelve un diccionario con una lista de activos
    con el nombre, tipo, precio de compra y venta de cada activo.
    '''
    with open('perfiles/asset/assets.json') as assets_json:
        assets_name = json.load(assets_json)
    assets_name = assets_name.get("availableAssets")
    assets_price = []
    assets = {}
    cap = 0
    if assets_name is not None:
        for asset in assets_name:
            name_as = 'perfiles/asset/'+str(asset.get("name"))+'.json'
            with open(name_as) as assets_price:
                price = json.load(assets_price)
                assets.update({(asset.get("type"), asset.get("name")): price})
    assets = assets.items()
    return assets


def quit_null_assets(assets):
    '''
    Quita de la lista de retorno aquellos activos que tengan un precio no
    definido o null.
    Retorna la lista de activos disponibles.
    '''
    assets_a = []
    for keys, values in assets:
        if values['sell'] is not None and values['buy'] is not None:
            assets_a.append(((keys[0],  keys[1]), {"sell": values['sell'],
                            "buy": values['buy']}))
    return assets_a


def open_json_history(name_asset):
    '''
    Abre y lee los archivos .json con el historial de cambios en los precios de
    compra y/o venta de cada activo.
    '''
    name_as = 'perfiles/asset/'+name_asset+'_history.json'
    with open(name_as) as assets_json:
        assets_name = json.load(assets_json)
    assets_name = assets_name.get("prices")
    return assets_name


def get_asset_history(asset_history, since_date, until_date):
    '''
    get_asset_history: Retorna una lista de datos referidos al historial del
    activo seleccionado entre las fechas elegidas por el usuario logueado.
    Si éste no tiene datos entre esas fechas, retorna el historial completo.
    '''
    history = []
    history_from_to = []
    i = 0
    for key, value in asset_history:
        day = asset_history[i][key]
        sell = asset_history[i][value][0]
        buy = asset_history[i][value][1]
        history.append([day, float(sell), float(buy)])
        i += 1
    for element in history:
        date = datetime.strptime(element[0], "%Y-%m-%d").date()
        since = datetime.strptime(since_date, "%Y-%m-%d").date()
        until = datetime.strptime(until_date, "%Y-%m-%d").date()
        if date >= since and date <= until:
            history_from_to.append([element[0], element[1], element[2]])
    if not history_from_to:
        for element in history:
            history_from_to.append([element[0], element[1], element[2]])
    return history_from_to
