from django.urls import path, re_path
from .views import activation, refreshTokenRest

urlpatterns = [
    re_path(r'^activate/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$', activation, name="activation"),
    path(r'^refreshToken/(?P<token>.+)/$', refreshTokenRest, name="refreshToken")
]
