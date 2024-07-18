from django.shortcuts import render
from django.http import HttpResponse

import os

def members(request):
    return HttpResponse("Hello World!")

def members_test(request):
    return HttpResponse(str(os.listdir()))
