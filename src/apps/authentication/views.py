from django.shortcuts import render

from django.http import HttpResponse, JsonResponse

def hello(request):
    return HttpResponse("Hello")


def hellojson(request):

    return JsonResponse({"message": "Hello from view", "username": "drbea"})