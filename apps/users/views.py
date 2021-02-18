from django.shortcuts import render, redirect
from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import force_text
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponseRedirect
from graphql_jwt.refresh_token.models import RefreshToken
from .models import User
from django.http import JsonResponse
import json
# Create your views here.

def activation(request, uidb64, token):
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, ObjectDoesNotExist):
        user = None
    
    if user is not None and (user.token == token):
        user.active = True
        user.token = ""
        user.save()
    else:
        return HttpResponseRedirect('https://pacome.com/404')
    
    return HttpResponseRedirect('https://pacome.com/login')

def refreshTokenRest(request, token):
    a = RefreshToken.objects.get(token=token, revoked__isnull=True)
    print(a)

    return JsonResponse(a)
