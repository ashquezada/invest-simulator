from django.test import TestCase, RequestFactory
from .models import CustomUser, Transaction, UserAsset, Alarm
from .views_alarm import low_alarms, list_alarms

"""
ACLARACIÓN:
En algunos tests a veces se simula ingresar a /buy/ o /sell/. Muchas veces
hacemos esto para obtener el request que necesitan los métodos para poder
pasarlo por parámetro y testearlos.
No necesariamente estamos haciendo una compra o venta de activos.
"""


class CustomUserTest(TestCase):

    def setUp(self):
        self.credentials = {
            "username": "usuario1",
            "email": "usuario1@example.com",
            "first_name": "Nombre1",
            "last_name": "Apellido1",
            "password": "user2458"
        }
        CustomUser.objects.create_user(**self.credentials)
        self.factory = RequestFactory()

    def test_login(self):
        '''
        Se verifica que el usuario creado anteriormente pueda loguearse.
        '''
        response = self.client.post('/login/', self.credentials, follow=True)
        self.assertTrue(response.context['user'].is_active)

    def test_login_false(self):
        '''
        Se verifica que un usuario no registrado no pueda iniciar sesión.
        '''
        data = {
            "username": "usuario2",
            "password": "user2458"
        }
        response = self.client.post('/login/', data, follow=True)
        self.assertFalse(response.context['user'].is_active)

    def test_initial_user_capital(self):
        '''
        Verificación del capital inicial del usuario logueado.
        '''
        custom_user = CustomUser.objects.get(pk=1)
        self.assertTrue(custom_user.is_active)
        assets = UserAsset.objects.all()
        my_assets = UserAsset.objects.filter(user=custom_user)
        current_money = CustomUser.calculate_capital(
                                assets, my_assets,
                                custom_user.virtual_money)
        self.assertEqual(current_money, 1000)

    def test_current_money_after_buy(self):
        '''
        Verificación del dinero actual del usuario logueado después de hacer
        una compra de un activo.
        '''
        custom_user = CustomUser.objects.get(pk=1)
        self.assertTrue(custom_user.is_active)
        price = [23, 25]
        request = self.factory.get('/buy/')
        request.user = custom_user
        CustomUser.update_money_user(request, 5, price[1],
                                     custom_user.virtual_money)
        self.assertEqual(custom_user.virtual_money, 875)

    def test_current_money_after_sell(self):
        '''
        Verificación del dinero actual del usuario logueado después de hacer
        una venta de un activo.
        '''
        custom_user = CustomUser.objects.get(pk=1)
        self.assertTrue(custom_user.is_active)
        price = [23, 25]
        # El usuario1 compra 5 acciones.
        request = self.factory.get('/buy/')
        request.user = custom_user
        CustomUser.update_money_user(request, 5, price[1],
                                     custom_user.virtual_money)
        # El usuario1 vende 3 acciones compradas.
        request = self.factory.get('/sell/')
        request.user = custom_user
        CustomUser.update_money_user(request, 3, price[0],
                                     custom_user.virtual_money)
        self.assertEqual(custom_user.virtual_money, 944)


class TransactionTest(TestCase):

    def setUp(self):
        self.credentials = {
            "username": "usuario1",
            "email": "usuario1@example.com",
            "first_name": "Nombre1",
            "last_name": "Apellido1",
            "password": "user2458"
        }
        CustomUser.objects.create_user(**self.credentials)
        self.factory = RequestFactory()
        self.client.post('/login/', self.credentials, follow=True)

    def test_add_one_buy_transaction_to_user(self):
        '''
        Se verifica que una nueva transacción de compra pueda guardarse
        correctamente para el usuario logueado.
        Solo agrega una transacción de compra.
        '''
        custom_user = CustomUser.objects.get(pk=1)
        self.assertTrue(custom_user.is_active)
        price = [23, 25]
        request = self.factory.get('/buy/')
        request.user = custom_user
        Transaction.addTransaction(request, price[0], price[1], 4, 1)
        user_transactions = Transaction.objects.filter(user=custom_user)
        self.assertEqual(len(user_transactions), 1)
        self.assertEqual(user_transactions[0].type_transaction, "compra")

    def test_add_one_sell_transaction_to_user(self):
        '''
        Se verifica que una nueva transacción de venta pueda guardarse
        correctamente para el usuario logueado.
        Solo se agrega una transacción de venta.
        '''
        custom_user = CustomUser.objects.get(pk=1)
        self.assertTrue(custom_user.is_active)
        price = [23, 25]
        request = self.factory.get('/sell/')
        request.user = custom_user
        Transaction.addTransaction(request, price[0], price[1], 4, 1)
        user_transactions = Transaction.objects.filter(user=custom_user)
        user_assets = UserAsset.objects.filter(user=custom_user)
        self.assertEqual(len(user_transactions), 1)
        self.assertEqual(user_transactions[0].type_transaction, "venta")

    def test_no_money_for_transaction(self):
        '''
        El usuario logueado quiere hacer una transacción de una compra de
        activos
        cuyo valor supera su dinero virtual.
        Se verifica que la transacción no se efectúa y dicho dinero sea el
        mismo.
        '''
        custom_user = CustomUser.objects.get(pk=1)
        current_money = custom_user.virtual_money
        self.assertTrue(custom_user.is_active)
        price = [23, 25]
        request = self.factory.get('/buy/')
        request.user = custom_user
        user_t_before = Transaction.objects.filter(user=custom_user)
        Transaction.addTransaction(request, price[0], price[1], 100, 1)
        user_t_after = Transaction.objects.filter(user=custom_user)
        self.assertEqual(len(user_t_before), len(user_t_after))
        self.assertEqual(custom_user.virtual_money, current_money)

    def test_sell_more_assets_than_current_amount(self):
        '''
        El usuario logueado quiere vender una cantidad de activos que es
        superior
        a la que actualmente tiene.
        Se verifica que la cantidad actual de ese activo no cambia debido a que
        la transacción no se realiza.
        '''
        custom_user = CustomUser.objects.get(pk=1)
        self.assertTrue(custom_user.is_active)
        price = [23, 25]
        request = self.factory.get('/buy/')
        request.user = custom_user
        # Agrego activos al usuario.
        UserAsset.addAsset(request, "Apple", 3, "Share", price[1], False)
        request = self.factory.get('/sell/')
        request.user = custom_user
        user_assets_before = UserAsset.objects.filter(user=custom_user)
        current_a_before = user_assets_before[0].total_amount
        Transaction.addTransaction(request, price[0], price[1], 10, 1)
        user_assets_after = UserAsset.objects.filter(user=custom_user)
        current_a_after = user_assets_after[0].total_amount
        self.assertEqual(current_a_before, current_a_after)


class UserAssetTest(TestCase):

    def setUp(self):
        self.credentials = {
            "username": "usuario1",
            "email": "usuario1@example.com",
            "first_name": "Nombre1",
            "last_name": "Apellido1",
            "password": "user2458"
        }
        CustomUser.objects.create_user(**self.credentials)
        self.factory = RequestFactory()
        self.client.post('/login/', self.credentials, follow=True)

    def test_add_asset_to_user(self):
        '''
        Se verifica que se pueda agregar un activo al usuario logueado.
        '''
        custom_user = CustomUser.objects.get(pk=1)
        self.assertTrue(custom_user.is_active)
        price = [23, 25]
        request = self.factory.get('/buy/')
        request.user = custom_user
        UserAsset.addAsset(request, "Apple", 3, "Share", price[1], False)
        user_assets = UserAsset.objects.filter(user=custom_user)
        self.assertEqual(len(user_assets), 1)

    def test_update_user_asset_amount(self):
        '''
        Verificación de poder actualizar la cantidad actual de activos para el
        usuario logueado.
        '''
        custom_user = CustomUser.objects.get(pk=1)
        self.assertTrue(custom_user.is_active)
        price = [23, 25]
        request = self.factory.get('/buy/')
        request.user = custom_user
        UserAsset.addAsset(request, "Apple", 3, "Share", price[1], True)
        user_assets = UserAsset.objects.filter(user=custom_user)
        UserAsset.update_asset(user_assets[0], 7, price[1], True)
        self.assertEqual(user_assets[0].total_amount, 10)

    def test_add_asset_to_user_with_negative_price(self):
        '''
        Se verifica que no se pueda agregar un activo con un precio negativo.
        Se comparan las cantidades antes de intentar agregar ese activo y
        después.
        '''
        custom_user = CustomUser.objects.get(pk=1)
        self.assertTrue(custom_user.is_active)
        price = [-23, -25]
        request = self.factory.get('/buy/')
        request.user = custom_user
        UserAsset.addAsset(request, "Apple", 2, "Share", 25, False)
        user_a_before = UserAsset.objects.filter(user=custom_user)
        UserAsset.addAsset(request, "Apple", 5, "Share", price[1], False)
        user_a_after = UserAsset.objects.filter(user=custom_user)
        self.assertEqual(user_a_before[0].total_amount,
                         user_a_after[0].total_amount)

    def test_first_position_for_user_ranking(self):
        '''
        Se comprueba que el único usuario registrado esté en primer lugar en el
        ranking.
        '''
        custom_user = CustomUser.objects.get(pk=1)
        self.assertTrue(custom_user.is_active)
        ranking = CustomUser.cons_ranking()
        self.assertEqual(ranking[0][0], 1)

    def test_second_position_for_user_ranking(self):
        '''
        Se comprueba que el usuario logueado está en el puesto 2 del ranking
        debido a que su capital es menor al del usuario recién registrado.
        '''
        CustomUser.objects.create(username="usuario2",
                                  email="usuario2@example.com",
                                  first_name="Nombre2",
                                  last_name="Apellido2",
                                  password="user2458")
        price = [23, 25]
        request = self.factory.get('/buy/')
        custom_user = CustomUser.objects.get(pk=2)
        request.user = custom_user
        # Agrego activos al usuario2, éste tendrá un capital mayor al usuario1.
        UserAsset.addAsset(request, "Apple", 5, "Share", price[1], False)
        ranking = CustomUser.cons_ranking()
        self.assertEqual(ranking[1][0], 2)


class AlarmTest(TestCase):

    def setUp(self):
        self.credentials = {
            "username": "usuario1",
            "email": "usuario1@example.com",
            "first_name": "Nombre1",
            "last_name": "Apellido1",
            "password": "user2458"
        }
        CustomUser.objects.create_user(**self.credentials)
        self.factory = RequestFactory()
        self.client.post('/login/', self.credentials, follow=True)

    def test_add_alarm_to_user(self):
        '''
        Verifica que se puede agregar correctamente una alarma para el usuario
        logueado.
        '''
        custom_user = CustomUser.objects.get(pk=1)
        self.assertTrue(custom_user.is_active)
        request = self.factory.get('/alarm/')
        request.user = custom_user
        Alarm.addAlarm(request, "Compra", "Superior", 25, 23, "Apple")
        user_alarms = Alarm.objects.filter(user=custom_user)
        self.assertEqual(len(user_alarms), 1)

    def test_low_alarm(self):
        '''
        Se comprueba que se pueda desactivar una alarma creada por el usuario
        logueado.
        '''
        custom_user = CustomUser.objects.get(pk=1)
        self.assertTrue(custom_user.is_active)
        request = self.factory.get('/alarm/')
        request.user = custom_user
        # El usuario1 crea dos alarmas.
        Alarm.addAlarm(request, "Compra", "Superior", 25, 23, "Apple")
        Alarm.addAlarm(request, "Venta", "Inferior", 16, 18, "Microsoft")
        user_alarms = list_alarms(request)
        # Comprobamos que tenga dos alarmas creadas.
        self.assertEqual(len(user_alarms), 2)
        # Desactivamos una alarma.
        low_alarms(request, 1)
        # Comprobamos que la lista de alarmas activadas ahora tiene longitud 1.
        user_alarms = Alarm.objects.filter(user=custom_user, type_alarm='low')
        self.assertEqual(len(user_alarms), 1)


class IntegrationTest(TestCase):

    def setUp(self):
        # Se registran tres usuarios.
        self.credentials = {
            "username": "usuario1",
            "email": "usuario1@example.com",
            "first_name": "Nombre1",
            "last_name": "Apellido1",
            "password": "user2458"
        }
        CustomUser.objects.create_user(**self.credentials)
        data_new_user = {
            "username": "usuario2",
            "email": "usuario2@example.com",
            "first_name": "Nombre2",
            "last_name": "Apellido2",
            "password": "user2458"
        }
        CustomUser.objects.create_user(**data_new_user)
        data_new_user_3 = {
            "username": "usuario3",
            "email": "usuario3@example.com",
            "first_name": "Nombre3",
            "last_name": "Apellido3",
            "password": "user2458"
        }
        CustomUser.objects.create_user(**data_new_user_3)
        self.factory = RequestFactory()

    def test_ranking_between_two_users(self):
        '''
        Se hace una prueba de ranking entre dos usuarios registrados en el
        sistema.
        Primero uno de ellos compra activos y se chequea que esté en primer
        lugar ya que aumenta su capital.
        Luego, el nuevo usuario realiza una compra de mayor cantidad de
        acciones y se comprueba que le ganó al usuario anterior y por lo tanto
        está en primer lugar.
        '''
        data_new_user = {
            "username": "usuario2",
            "password": "user2458"
        }
        # usuario1 inicia sesión.
        self.client.post('/login/', self.credentials, follow=True)
        user_logged = CustomUser.objects.get(pk=1)
        self.assertTrue(user_logged.is_active)
        # usuario1 compra 5 acciones.
        request = self.factory.get('/buy/')
        request.user = user_logged
        price = [23, 25]
        UserAsset.addAsset(request, "Microsoft", 5, "Share", price[1], False)
        ranking = CustomUser.cons_ranking()
        # usuario1 está primero en el ranking porque gana con su capital.
        self.assertEqual(ranking[0][1], "usuario1")
        # usuario2 inicia sesión.
        self.client.post('/login/', data_new_user, follow=True)
        user_logged = CustomUser.objects.get(pk=2)
        self.assertTrue(user_logged.is_active)
        request = self.factory.get('/buy/')
        request.user = user_logged
        # usuario2 compra 10 acciones.
        UserAsset.addAsset(request, "Microsoft", 10, "Share", price[1], False)
        ranking = CustomUser.cons_ranking()
        # usuario1 ahora pasó a estar segundo en el ranking.
        self.assertEqual(ranking[0][1], "usuario2")

    def test_random_1(self):
        '''
        Se comprueban funcionalidades aleatorias.
        El usuario1 está logueado, realiza una compra de activos, se calcula
        su dinero virtual.
        El usuario1 configura dos alarmas. Luego realiza la venta de 2 activos
        comprados anteriormente y se calcula su dinero virtual.
        El usuario1 dehabilita una alarma.
        '''
        # usuario1 inicia sesión.
        self.client.post('/login/', self.credentials, follow=True)
        user_logged = CustomUser.objects.get(pk=1)
        self.assertTrue(user_logged.is_active)
        # usuario1 compra 6 acciones.
        request = self.factory.get('/buy/')
        request.user = user_logged
        price = [23, 25]
        UserAsset.addAsset(request, "Microsoft", 6, "Share", price[1], False)
        # Actualizamos el dinero virtual del usuario1.
        CustomUser.update_money_user(request, 6, price[1],
                                     user_logged.virtual_money)
        self.assertEqual(user_logged.virtual_money, 850)
        # usuario1 configura dos alarmas.
        request = self.factory.get('/alarm/')
        request.user = user_logged
        Alarm.addAlarm(request, "Compra", "Superior", 25, 23, "Apple")
        Alarm.addAlarm(request, "Venta", "Inferior", 14, 10, "Microsoft")
        # Chequeamos que se guardan ambas alarmas.
        user_alarms = Alarm.objects.filter(user=user_logged)
        self.assertEqual(len(user_alarms), 2)
        # usuario1 vende 2 activos.
        request = self.factory.get('/sell/')
        request.user = user_logged
        CustomUser.update_money_user(request, 2, price[0],
                                     user_logged.virtual_money)
        self.assertEqual(user_logged.virtual_money, 896)
        # usuario1 da de baja una alarma.
        request = self.factory.get('/alarm/')
        request.user = user_logged
        low_alarms(request, 1)
        # Se comprueba que la alarma fue deshabilitada.
        user_alarms = Alarm.objects.filter(user=user_logged, type_alarm="low")
        self.assertEqual(len(user_alarms), 1)

    def test_random_2(self):
        '''
        Se chequean funcionalidades aleatorias distintas al test random 1.
        Se utilizan 3 usuarios para ir viendo como van cambiando de posiciones
        según las compras y ventas que realiza cada uno.
        '''
        data_new_user = {
            "username": "usuario2",
            "password": "user2458"
        }
        data_new_user = {
            "username": "usuario3",
            "password": "user2458"
        }
        # usuario1 inicia sesión.
        self.client.post('/login/', self.credentials, follow=True)
        user_logged = CustomUser.objects.get(pk=1)
        self.assertTrue(user_logged.is_active)
        # usuario1 compra 10 acciones.
        request = self.factory.get('/buy/')
        request.user = user_logged
        price = [23, 25]
        UserAsset.addAsset(request, "Microsoft", 10, "Share", price[1], False)
        # Actualizamos el dinero virtual del usuario1.
        CustomUser.update_money_user(request, 10, price[1],
                                     user_logged.virtual_money)
        self.assertEqual(user_logged.virtual_money, 750)
        # usuario2 inicia sesión.
        self.client.post('/login/', data_new_user, follow=True)
        user_logged = CustomUser.objects.get(pk=2)
        self.assertTrue(user_logged.is_active)
        request = self.factory.get('/buy/')
        request.user = user_logged
        # usuario2 compra 10 acciones.
        UserAsset.addAsset(request, "Apple", 20, "Share", price[1], False)
        # Actualizamos su moneda virtual.
        CustomUser.update_money_user(request, 20, price[1],
                                     user_logged.virtual_money)
        self.assertEqual(user_logged.virtual_money, 500)
        # usuario1 está en segundo puesto.
        ranking = CustomUser.cons_ranking()
        self.assertEqual(ranking[1][1], "usuario1")
        # El usuario3 tiene que estar en primer lugar.
        self.assertEqual(ranking[0][1], "usuario3")
        # usuario2 vende todos sus activos.
        request = self.factory.get('/sell/')
        request.user = user_logged
        CustomUser.update_money_user(request, 20, price[0],
                                     user_logged.virtual_money)
        self.assertEqual(user_logged.virtual_money, 960)
        # usuario2 pasa a estar en segundo lugar dejando último al usuario1.
        ranking = CustomUser.cons_ranking()
        self.assertEqual(ranking[1][1], "usuario2")
