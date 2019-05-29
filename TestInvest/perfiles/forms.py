from django import forms
from django.contrib.auth.forms import (
  UserCreationForm, AuthenticationForm, PasswordChangeForm)
from django.contrib.auth.models import User
from .models import CustomUser, UserAsset, Alarm
from django.contrib.auth.forms import UserChangeForm
from django.core.files.images import get_image_dimensions
from django.forms import ModelForm


class SignUpForm(UserCreationForm):
    '''
    Formulario para el registro de usuarios.
    Permite que el usuario pueda rellenarlo con sus datos, que éstos sean
    validados.
    '''
    first_name = forms.CharField(label="Nombre", max_length=140, required=True)
    last_name = forms.CharField(label="Apellido", max_length=140,
                                required=True)
    email = forms.EmailField(required=True, widget=forms.TextInput(attrs={
                            'placeholder': 'usuario@usuario.com'
                        })
                )
    email2 = forms.EmailField(label='Email (confirmacion)', required=True,
                              widget=forms.TextInput(
                                attrs={
                                    'placeholder': 'usuario@usuario.com'
                                })
                              )

    def clean_email2(self):
        email = self.cleaned_data.get("email")
        email2 = self.cleaned_data.get("email2")
        if email and email != email2:
            raise forms.ValidationError("Los 2 campos de emails no coinciden")
        return email2

    class Meta:
        model = CustomUser
        fields = (
            'username',
            'email',
            'email2',
            'first_name',
            'last_name',
            'password1',
            'password2',
            'avatar',
        )


class UpdateProfileForm(forms.ModelForm):
    '''
    Formulario que permite al usuario poder actualizar sus datos personales
    para su perfil. Posteriormente estos datos son válidados.
    '''
    first_name = forms.CharField(label="Nombre", max_length=140, required=True)
    last_name = forms.CharField(label="Apellido", max_length=140,
                                required=True)
    email = forms.EmailField(required=True)

    class Meta:
        model = CustomUser
        fields = (
            'first_name',
            'last_name',
            'email',
            'avatar',
        )


class BuyForm(ModelForm):
    """ Formulario necesario para comprar un activo.
        Es necesario llenarlo con nombre del activo, total a comprar y su
        visibilidad para los otros usuarios.
    """
    VISIBILITY = ((False, 'No'), (True, 'Si'))
    name = forms.CharField(required=False, label="Nombre del Activo")
    total_amount = forms.IntegerField(label="Cantidad Activo", required=False)
    visibility = forms.ChoiceField(choices=VISIBILITY, label="Visible")

    class Meta:
        model = UserAsset
        fields = (
            'name',
            'total_amount',
            'visibility',
        )


class SellForm(forms.Form):
    '''Formulario necesario para vender un activo.
       Es necesario llenarlo con nombre del activo, total a vender, precio de
       venta y el dinero virtual.
    '''
    name = forms.CharField(required=False, label="Nombre del Activo")
    total_amount = forms.IntegerField(label="Cantidad Activo", required=False)
    price_sell = forms.CharField(label="Precio de Venta", required=False)
    virtual_money = forms.CharField(
      label="Dinero Liquido obtenido", required=False)


class DateInput(forms.DateTimeInput):
    '''
    Widget necesario que muestra el calendario.
    '''
    input_type = 'date'


class TimeInput(forms.TimeInput):
    '''
    Widget necesario que permite elegir un horario.
    '''
    input_type = 'time'


class AssetForm(forms.Form):
    '''
    Formulario necesario para que el usuario elija las fechas y el activo
    para el cual desea saber su historial.
    '''
    name = forms.CharField(required=False)
    since = forms.CharField(widget=DateInput())
    time_since = forms.CharField(widget=TimeInput())
    until = forms.CharField(widget=DateInput())
    time_until = forms.CharField(widget=TimeInput())

    def __init__(self, *args, **kwargs):
        super(AssetForm, self).__init__(*args, **kwargs)
        self.fields['name'].label = 'Nombre'
        self.fields['since'].label = 'Desde'
        self.fields['time_since'].label = 'Hora'
        self.fields['until'].label = 'Hasta'
        self.fields['time_until'].label = 'Hora'


class AlarmForm(ModelForm):
    '''
    Formulario que permite al usuario configurar una alarma.
    Le permite elegir un umbral, tipo de cotización esperada, entre otros.
    '''
    type_quote = forms.ChoiceField(required=True, choices=(
      ('buy', 'Compra'), ('sell', 'Venta')))
    type_umbral = forms.ChoiceField(required=True, choices=(
      ('less', 'Inferior'), ('top', 'Superior')))

    def __init__(self, *args, **kwargs):
        super(AlarmForm, self).__init__(*args, **kwargs)
        self.fields['type_quote'].label = 'Tipo de Cotización'
        self.fields['type_umbral'].label = 'Tipo de Umbral'
        self.fields['previous_quote'].label = 'Valor actual'
        self.fields['previous_quote'].widget = forms.TextInput(attrs={
          'placeholder': 'Elija un Activo Disponible'})
        self.fields['umbral'].label = 'Precio'
        self.fields['name_asset'].label = 'Nombre del Activo'
        self.fields['name_asset'].widget = forms.TextInput(attrs={
          'placeholder': 'Elija un Activo Disponible'})

    class Meta:
        model = Alarm
        fields = (
            'type_quote',
            'type_umbral',
            'previous_quote',
            'umbral',
            'name_asset',
        )


class LowAlarmForm(forms.Form):
    """ Formulario necesario para dar de baja una alarma.
        Es necesario llenarlo con nombre del activo, el tipo de umbral y el
        precio del umbral.
    """
    id = forms.IntegerField()

    def __init__(self, *args, **kwargs):
        super(LowAlarmForm, self).__init__(*args, **kwargs)
        self.fields['id'].widget = forms.HiddenInput()


class Visibility(ModelForm):
    '''Formulario para la visibilidad de un activo de un usuario frente a
       otros usuarios.
       Se necesita nombre del activo y la visibilidad que solo puede ser
       falsa o verdadera.
    '''
    VISIBILITY = ((False, 'No'), (True, 'Si'))
    name = forms.CharField(required=False, label="Nombre del Activo")
    visibility = forms.ChoiceField(required=False, choices=VISIBILITY,
                                   label="Visible")

    def __init__(self, *args, **kwargs):
        super(Visibility, self).__init__(*args, **kwargs)
        self.fields['name'].widget = forms.HiddenInput()
        self.fields['visibility'].widget = forms.HiddenInput()

    class Meta:
        model = UserAsset
        fields = (
            'name',
            'visibility'
        )
