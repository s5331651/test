from django.urls import path
from . import views

urlpatterns = [

    path('', views.home),
    path('grafana/', views.grafana_dashboard, name='grafana_dashboard'),

]