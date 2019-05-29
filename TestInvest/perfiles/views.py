# -- coding: utf-8 --
from __future__ import unicode_literals
from django.shortcuts import (render, render_to_response, get_object_or_404,
                              redirect)
from django.contrib.auth import login, authenticate, update_session_auth_hash
from django.contrib.auth.views import LoginView, LogoutView
from django.views.generic import CreateView, TemplateView, UpdateView
from django.contrib.auth.forms import PasswordChangeForm
from .forms import SignUpForm, UpdateProfileForm, Visibility
from django.contrib import messages
from .models import CustomUser, UserAsset, Transaction
from .data_api import open_jsons, quit_null_assets
from .views_alarm import get_data_of_alarm
import threading
import time
from django.template import RequestContext
from datetime import datetime
from django.core.mail import EmailMessage, send_mail
from django.contrib.auth.decorators import login_required


class SignUpView(CreateView):
    model = CustomUser
    form_class = SignUpForm
    template_name = 'perfiles/signup.html'

    def form_valid(self, form):
        form.save()
        usuario = form.cleaned_data.get('username')
        password = form.cleaned_data.get('password1')
        usuario = authenticate(username=usuario, password=password)
        return render(self.request, 'perfiles/signup.html', {'form': form})


def WelcomeView(request):
    """ welcomeView: Envia a la pagina de inicio, con el puesto en el ranking
        y el dinero liquido del usuario logueado, o para que inicie sesion o
        se registre.
    """
    if request.user.is_authenticated:
        return render(request, 'perfiles/home.html',
                      {'pos_ranking': CustomUser.rank_virtualm(request)})
    else:
        return render(request, 'perfiles/home.html')


class ProfileView(TemplateView):
    template_name = 'perfiles/profile.html'


def profileView(request):
    """ profileView: Muestra en la pagina de perfil el puesto en el ranking y
        el dinero liquido del usuario logueado
    """
    pos_ranking = CustomUser.rank_virtualm(request)
    return render(request, 'perfiles/profile.html',
                  {'pos_ranking': pos_ranking})


def change_password(request):
    '''change_password: Cambia la contraseña del usuario logueado
    '''
    pos_ranking = CustomUser.rank_virtualm(request)
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'perfiles/change_password.html',
                  {'form': form, 'pos_ranking': pos_ranking})


class SignInView(LoginView):
    template_name = 'perfiles/login.html'


class SignOutView(LogoutView):
    pass


class UpdateProfileView(UpdateView):
    model = CustomUser
    template_name = 'perfiles/update_profile.html'
    form_class = UpdateProfileForm

    def get_object(self):
        """
        get_object: Retorna la información del usuario logueado. En caso de no
        encontrarlo, devuelve error 404 not found.
        """
        return get_object_or_404(CustomUser, pk=self.request.user.id)


def addOperation(request, assets_user, nametype, name_form,
                 total_amount, sell, buy, virtual_money, visibility):
    """ addOperation: Agrega una operacion de compra a la base de datos.
    """
    if assets_user.exists():
        for asset in assets_user:
            if (nametype[1] == asset.name):
                UserAsset.update_asset(asset, total_amount, sell, visibility)
                transaction = Transaction.addTransaction(
                  request, sell, buy, total_amount, asset.id)
                CustomUser.update_money_user(
                  request, total_amount, sell, virtual_money)
    elif (nametype[1] == name_form):
        asset_user = UserAsset.addAsset(request, name_form, total_amount,
                                        nametype[0], buy, visibility)
        transaction = Transaction.addTransaction(
          request, sell, buy, total_amount, asset_user.id)
        CustomUser.update_money_user(
          request, total_amount, buy, virtual_money)
    return virtual_money


def mytransactions(request):
    """ mytransactions: devuelve las transacciones del usuario logeado.
    """
    pos_ranking = CustomUser.rank_virtualm(request)
    my_transactions = Transaction.objects.filter(user=request.user.id)
    my_transactions = my_transactions.order_by('-date')
    return render_to_response(
      'perfiles/transaction_history.html', {'my_transactions': my_transactions,
                                            'user': request.user,
                                            'pos_ranking': pos_ranking})


def ranking(request):
    """ ranking: Renderiza la lista.
    """
    pos_ranking = CustomUser.rank_virtualm(request)
    list_cap = CustomUser.cons_ranking()
    users = CustomUser.objects.all()
    return render_to_response('perfiles/see_ranking.html',
                              {'lista_capital': list_cap,
                               'user': request.user,
                               'pos_ranking': pos_ranking})


def visibility_investments(request):
    """visibility_investments: Renderiza las transacciones visibles.
    """
    pos_ranking = CustomUser.rank_virtualm(request)
    ranking = CustomUser.cons_ranking()
    all_assets = open_jsons()
    assets_a = quit_null_assets(all_assets)
    investments_v = UserAsset.objects.filter(visibility=True,
                                             total_amount__gt=0)
    datas = []
    for invest in investments_v:
        assets = UserAsset.objects.filter(user_id=invest.user_id,
                                          name=invest.name)
        for asset in assets:
            ult_trans = Transaction.objects.filter(user_id=invest.user_id,
                                                   type_transaction='compra',
                                                   user_asset_id=asset.id)
            ult_trans = ult_trans.last()
            datas.append([invest.user_id, asset.name, ult_trans.date,
                          ult_trans.value_sell])
    return render_to_response('perfiles/visibility_investments.html',
                              {'user': request.user,
                               'investments_v': investments_v,
                               'ranking': ranking, 'pos_ranking': pos_ranking,
                               'datas': datas, 'assets': assets_a})


'''Funciones para consultar los cambios en los datos de la API y enviar mail
   al usuario que configuró su alarma
'''


def consult_alarm_forever():
    '''consult_alarm_forever: Llama a la función get_data_of_alarm cada 15 segundos
    '''
    while True:
        get_data_of_alarm()
        time.sleep(15)


def hilo():
    '''hilo: Se define como hilo principal a la función consult_alarm_forever()
    '''
    hilo = threading.Thread(target=consult_alarm_forever)
    hilo.setDaemon(True)
    hilo.start()


hilo()
'''hilo(): se debe ejecutar al iniciar el programa'''
