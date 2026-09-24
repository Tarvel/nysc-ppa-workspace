from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.dashboard_view, name='dashboard'),
    path('search/', views.search_view, name='search'),
    path('api/v1/capture/', views.api_capture_view, name='api_capture'),
]
