from django.urls import path
from . import views

app_name = 'contacts'

urlpatterns = [
    path('org/<int:org_id>/add/', views.create_contact_view, name='create'),
    path('<int:pk>/delete/', views.delete_contact_view, name='delete'),
]
