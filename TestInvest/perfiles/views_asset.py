# -- coding: utf-8 --
from __future__ import unicode_literals
from django.shortcuts import (render, render_to_response, get_object_or_404,
                              redirect)
from django.contrib.auth import login, authenticate, update_session_auth_hash
from django.contrib.auth.views import LoginView, LogoutView
from django.views.generic import CreateView, TemplateView, UpdateView
from django.contrib.auth.forms import PasswordChangeForm
from .forms import BuyForm, SellForm, AssetForm, Visibility
from django.contrib import messages
from .data_api import (open_jsons, quit_null_assets, open_json_history,
                       get_asset_history)
from .models import CustomUser, UserAsset, Transaction
from .views import addOperation
import json


def show_assets(request):
    '''show_assets: Muestra los activos que posee la API:
       nombre del activo, valor de compra, valor de venta y tipo.
    '''
    pos_ranking = CustomUser.rank_virtualm(request)
    user = request.user
    virtual_money = request.user.virtual_money
    my_assets = UserAsset.objects.filter(user=request.user.id)
    assets = open_jsons()
    assets_a = quit_null_assets(assets)
    mj = False
    cap = CustomUser.calculate_capital(assets, my_assets, virtual_money)
    if request.get_full_path() == '/buy/':
        if request.method == 'POST':
            form = BuyForm(request.POST)
            virtual_money, assets, mj = buy_assets(
              request, form, assets, virtual_money, mj)
        else:
            form = BuyForm()
        return render(request, 'perfiles/buy.html', {
          'assets': assets_a, 'virtual_money': virtual_money, 'form': form,
          'mj': mj, 'pos_ranking': pos_ranking})
    if request.get_full_path() == '/price/':
        return render_to_response('perfiles/price.html', {'assets': assets_a,
                                  'user': user, 'pos_ranking': pos_ranking})
    if request.get_full_path() == '/wallet/':
        return render_to_response('perfiles/wallet.html', {
          'assets': assets, 'user': user, 'my_assets': my_assets,
          'capital': cap, 'pos_ranking': pos_ranking})


def assets_history(request):
    '''assets_history: Devuelve el historial de cotización de un activo dentro
       de dos fechas determinadas
    '''
    pos_ranking = CustomUser.rank_virtualm(request)
    assets = open_jsons()
    assets_a = quit_null_assets(assets)
    form = AssetForm()
    if request.method == 'POST':
        form = AssetForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data.get("name")
            since_date = form.cleaned_data.get("since")
            until_date = form.cleaned_data.get("until")
            asset_history = open_json_history(name)
            is_history = True
            history_from_to = []
            history_from_to = get_asset_history(
              asset_history, since_date, until_date)
            grap_history = [["Fecha", "Venta", "Compra"]]
            grap_history += history_from_to
            return render(request, 'perfiles/assets_history.html', {
                      'history': history_from_to, 'is_history': is_history,
                      'name_asset': name, 'grap': json.dumps(grap_history),
                      'pos_ranking': pos_ranking})
    return render(request, 'perfiles/assets_history.html',
                  {'assets': assets_a, 'form': form,
                   'pos_ranking': pos_ranking})


def show_my_assets(request):
    '''show_my_assets: Muestra los activos que posee el usuario logueado con:
       nombre del activo, cantidad, tipo, valor de adquisición, valor de
       compra, valor de venta y su estado de visibilidad
       Y tambien se configura la visibilidad del activo frente a otros usuarios
    '''
    pos_ranking = CustomUser.rank_virtualm(request)
    user = request.user
    virtual_money = request.user.virtual_money
    my_assets = UserAsset.objects.filter(user=request.user.id)
    my_assets = my_assets.filter(total_amount__gt=0)
    assets = open_jsons()
    cap = CustomUser.calculate_capital(assets, my_assets, virtual_money)
    form = Visibility(request.POST)
    if form.is_valid():
        name = form.cleaned_data.get("name")
        visibility = form.cleaned_data.get("visibility")
        for asset in my_assets:
            if (name == asset.name):
                asset.visibility = visibility
                asset.save()
                my_assets = UserAsset.objects.filter(user=request.user.id)
                my_assets = my_assets.filter(total_amount__gt=0)
                return render(request, 'perfiles/wallet.html',
                                       {'assets': assets, 'user': user,
                                        'my_assets': my_assets,
                                        'capital': cap, 'form': form,
                                        'pos_ranking': pos_ranking})
    return render(request, 'perfiles/wallet.html',
                           {'assets': assets, 'user': user,
                            'my_assets': my_assets, 'capital': cap,
                            'form': form, 'pos_ranking': pos_ranking})


def buy_assets(request, form, assets, capital, mj):
    """ buy_assets: Compra activos disponibles.
    """
    virtual_money = request.user.virtual_money
    if form.is_valid():
        name = form.cleaned_data.get("name")
        total_amount = form.cleaned_data.get("total_amount")
        visibility = form.cleaned_data.get("visibility")
        assets_user = UserAsset.objects.filter(user=request.user.id, name=name)
        for nametype, prices in assets:
            if nametype[1] == name and (prices['sell'] is None
                                        or prices['buy'] is None):
                messages.add_message(
                  request, messages.INFO, 'El Activo seleccionado ya no se'
                  'encuentra  disponible, no se pudo concretar la compra. Para'
                  ' ver la actual lista de activos recargue la pagina')
                break
            sell = prices['sell']
            buy = prices['buy']
            addOperation(request, assets_user, nametype, name,
                         total_amount, sell, buy, virtual_money, visibility)
            virtual_money = request.user.virtual_money
            mj = True
        return virtual_money, assets, mj


def sell_assets(request):
    '''sell_assets: Vende los activos que dispone el usuario
    '''
    pos_ranking = CustomUser.rank_virtualm(request)
    user = CustomUser
    virtual_money = request.user.virtual_money
    assets = open_jsons()
    form = SellForm(request.POST)
    if form.is_valid():
        name = form.cleaned_data.get("name")
        total_amount = form.cleaned_data.get("total_amount")
        my_assets = UserAsset.objects.filter(user=request.user.id, name=name)
        for names, datas in assets:
            if my_assets.exists():
                for asset in my_assets:
                    if ((names[1] == asset.name) & (asset.total_amount > 0)):
                        asset.total_amount = asset.total_amount - total_amount
                        asset.save()
                        transaction = Transaction.addTransaction(
                                      request, datas['sell'], datas['buy'],
                                      total_amount, asset.id)
                        virtual_money = CustomUser.update_money_user(
                          request, total_amount, datas['buy'], virtual_money)
                        return redirect('http://localhost:8000/wallet')
    return render(request, 'perfiles/salle.html', {
                  'assets': assets, 'my_assets': my_assets,
                  'virtual_money': virtual_money, 'form': form,
                  'pos_ranking': pos_ranking})
