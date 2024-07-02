from django.urls import path
from . import views  # Import views module from your app
from django.contrib.auth import views as auth_views
from .views import influxdb_latest_view

urlpatterns = [
    path('', views.home_view, name='home'),
    path('login/', auth_views.LoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('device/<int:id>/', views.device_detail, name='device_detail'), # Import and use the device_list view
    path('influxdb/', influxdb_latest_view, name='influxdb_latest'),
]