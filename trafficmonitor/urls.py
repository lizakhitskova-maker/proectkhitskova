# БЛОК ПОДКЛЮЧЕНИЯ МОДУЛЕЙ
from django.urls import path
from . import views
# БЛОК ОПРЕДЕЛЕНИЯ URL-МАРШРУТОВ
urlpatterns = [
    path('', views.index, name='index')
]