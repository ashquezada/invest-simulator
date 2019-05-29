from django.conf.urls import url
from django.contrib import admin
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from perfiles.views import (SignUpView, SignInView, SignOutView,
                            UpdateProfileView, ProfileView)
from TestInvest import settings
from perfiles import views, views_asset, views_alarm
from django.conf.urls.static import static


def anonymous_required(func):
    def as_view(request, *args, **kwargs):
        redirect_to = kwargs.get('next', settings.LOGIN_REDIRECT_URL)
        if request.user.is_authenticated:
            return redirect(redirect_to)
        response = func(request, *args, **kwargs)
        return response
    return as_view


urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^$', views.WelcomeView, name='home'),
    url(r'^profile/$', login_required(views.profileView), name='profile'),
    url(r'^signup/$', anonymous_required(SignUpView.as_view()),
        name='sign_up'),
    url(r'^login/$', anonymous_required(SignInView.as_view()),
        name='sign_in'),
    url(r'^logout/$', SignOutView.as_view(), name='sign_out'),
    url(r'^password/$', login_required(views.change_password),
        name='change_password'),
    url(r'^profile/$', ProfileView.as_view(), name='profile'),
    url(r'^update_profile/$', UpdateProfileView.as_view(
        success_url='/profile'), name='update_profile'),
    url(r'^price/$', login_required(views_asset.show_assets), name='price'),
    url(r'^buy/$', login_required(views_asset.show_assets), name='buy'),
    url(r'^wallet/$', login_required(views_asset.show_my_assets), name='wallet'),
    url(r'^salle/$', login_required(views_asset.sell_assets), name='salle'),
    url(r'^transactionhistory/$', login_required(views.mytransactions),
                   name='transaction_history'),
    url(r'^ranking/$', login_required(views.ranking), name='ranking'),
    url(r'^assetshistory/$', login_required(views_asset.assets_history),
        name='assets_history'),
    url(r'^alarm/$', login_required(views_alarm.config_alarm),
                   name='alarm'),
    url(r'^view_alarm/$', login_required(views_alarm.view_alarm),
                   name='view_alarm'),
   url(r'^visibilityinvestments/$', login_required(views.visibility_investments),
                   name='visibility_investments'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
