from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard_view, name='dashboard'),
    path('add/', views.add_device_view, name='add_device'),
    path('search/', views.search_view, name='search_device'),
    path('delete/<str:device_id>/', views.delete_device_view, name='delete_device'),
    path('charts/', views.charts_view, name='charts'),
]