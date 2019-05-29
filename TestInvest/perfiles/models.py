from __future__ import unicode_literals
from django.db import models
from django.contrib.auth.models import User, AbstractUser
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.validators import MinValueValidator
from django.utils import timezone
from .data_api import (open_jsons, quit_null_assets, open_json_history,
                       get_asset_history)


class CustomUser(AbstractUser):
    '''
    Modelo usuario que reemplaza al tradicional utilizado internamente por
    Django.
    Se le agregan atributos como avatar y moneda virtual.
    '''
    avatar = models.ImageField(upload_to='perfiles/',
                               default='perfiles/default.jpg')
    virtual_money = models.FloatField(
        validators=[MinValueValidator(0.0)], blank=None, default=1000
        )

    def __str__(self):
        return self.email

    def calculate_capital(assets, my_assets, virtual_money):
        '''
        calculate_capital: Calcula el capital del usuario logueado tomando
        los activos que tiene y su cotización actual más su dinero virtual.
        '''
        cap = 0
        for name, data in assets:
            for asset in my_assets:
                if (asset.name == name[1] and data['sell'] is not None):
                    cap += asset.total_amount * data['sell']
        cap += virtual_money
        return cap

    def update_money_user(request, total_amount, data, virtual_money):
        """ update_money_user: Actualiza el dinero virtual del usuario.
            update_money_user = update_money_user +/- total de activo en
            operacion multiplicado la cotizacion
        """
        if request.get_full_path() == '/buy/':
            virtual_money -= total_amount * data
        else:
            virtual_money += total_amount * data
        request.user.virtual_money = virtual_money
        request.user.save()

    def cons_ranking():
        """ cons_ranking: Brinda la lista de puestos en el ranking de los usuarios
        con su capital.
        [[posicion, nombre usuario, capital]]
        """
        assets = open_jsons()
        dict_cap = {}
        users = CustomUser.objects.all()
        i = 1
        ranking = []
        for user in users:
            assets_users = UserAsset.objects.filter(user=user.id)
            capital = CustomUser.calculate_capital(assets, assets_users,
                                                   user.virtual_money)
            dict_cap.update({user.username: capital})
        dict_items = dict_cap.items()
        list_cap = sorted(dict_items, key=lambda x: x[1], reverse=True)
        total_user = CustomUser.objects.count()
        for i in range(total_user):
            ranking.append((i+1,) + list_cap[i])
        return ranking

    def rank_virtualm(request):
        """ rank_virtualm: Muestra la posicion en el ranking del usuario logueado.
        """
        ranking = CustomUser.cons_ranking()
        pos_rank = 0
        for rank in ranking:
            if request.user.username == rank[1]:
                request.user.pos_ranking = rank[0]
                request.user.save()
        return request.user.pos_ranking


@receiver(post_save, sender=User)
def crear_usuario_perfil(sender, instance, created, **kwargs):
    if created:
        Perfil.objects.create(usuario=instance)


@receiver(post_save, sender=User)
def guardar_usuario_perfil(sender, instance, **kwargs):
    instance.perfil.save()


class UserAsset(models.Model):
    '''
    Modelo de activo para el usuario.
    Se forma una relación varios - uno con el usuario registrado en el sistema.
    '''
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    name = models.CharField(max_length=30)
    type_asset = models.CharField(max_length=30)
    total_amount = models.PositiveIntegerField(blank=None)
    old_unit_value = models.FloatField(
        validators=[MinValueValidator(0.0)], blank=None)
    visibility = models.BooleanField(default=False)

    def addAsset(request, name, total_amount, type_asset, old_unit_value,
                 visibility):
        """ addAsset: Agrega un activo a la Base de Datos.
        """
        asset = UserAsset.objects.create(
                  user_id=request.user.id, name=name,
                  total_amount=total_amount,
                  type_asset=type_asset, old_unit_value=old_unit_value,
                  visibility=visibility)
        asset.save()
        return asset

    def update_asset(asset, total_amount, data, visibility):
        """ update_asset: Actualiza la cantidad de un activo.
        """
        asset.total_amount += total_amount
        asset.old_unit_value = data
        asset.visibility = visibility
        asset.save()


class Transaction(models.Model):
    '''
    Modelo de transacción para cuando un usuario registrado y logueado realiza
    una compra o una venta de un activo.
    '''
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    user_asset = models.ForeignKey(UserAsset, on_delete=models.CASCADE)
    type_transaction = models.CharField(max_length=30)
    value_buy = models.FloatField(
        validators=[MinValueValidator(0.0)], blank=None
        )
    value_sell = models.FloatField(
        validators=[MinValueValidator(0.0)], blank=None
        )
    amount = models.PositiveIntegerField(blank=None)
    date = models.DateTimeField(max_length=50)

    def addTransaction(request, value_buy, value_sell, total_amount,
                       user_asset_id):
        """ addTransaction: Agrega una transaccion a la Base de Datos.
        """
        if request.get_full_path() == '/buy/':
            type_t = str("compra")
        else:
            type_t = str("venta")
        transaction = Transaction.objects.create(user_id=request.user.id,
                                                 user_asset_id=user_asset_id,
                                                 value_buy=value_buy,
                                                 value_sell=value_sell,
                                                 amount=total_amount,
                                                 date=timezone.now(),
                                                 type_transaction=type_t)
        transaction.save()
        return transaction


class Alarm(models.Model):
    '''
    Modelo de alarma. Se relaciona con varios - uno con el usuario registrado.
    '''
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    name_asset = models.CharField(max_length=30)
    type_alarm = models.CharField(max_length=30)
    type_quote = models.CharField(max_length=30)
    type_umbral = models.CharField(max_length=30)
    previous_quote = models.FloatField(
        validators=[MinValueValidator(0.0)], blank=None)
    umbral = models.FloatField(
        validators=[MinValueValidator(0.0)], blank=None)
    email_send = models.BooleanField(default=False)

    def addAlarm(request, type_quote, type_umbral,
                 umbral, previous_quote, name_asset):
        '''
        addAlarm: Crea y guarda una alarma en la base de datos.
        '''
        alarm = Alarm.objects.create(
                    user_id=request.user.id, name_asset=name_asset,
                    type_alarm="high", type_quote=type_quote,
                    type_umbral=type_umbral, umbral=umbral,
                    previous_quote=previous_quote)
        alarm.save()
        return alarm
