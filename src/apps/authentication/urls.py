from django.urls import path
from . import views

app_name = ""

urlpatterns = [
    path("json", views.hellojson, name = "json_hello"),
]