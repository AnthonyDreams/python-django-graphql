from django.shortcuts import render
from django.conf import settings
from django.http import  Http404
from .seed import TypeSeed

def RunProductSeed(request):
    if settings.DEBUG:
        TypeSeed()
    else:
        raise Http404
# Create your views here.
