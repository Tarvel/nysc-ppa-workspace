from django.urls import path
from . import views

app_name = 'organizations'

urlpatterns = [
    path('', views.organization_list_view, name='list'),
    path('<int:pk>/', views.organization_detail_view, name='detail'),
    path('quick-add/', views.quick_add_view, name='quick_add'),
    path('<int:pk>/add-note/', views.add_note_view, name='add_note'),
    path('<int:pk>/research/', views.trigger_research_view, name='trigger_research'),
    path('<int:pk>/update-status/', views.update_status_view, name='update_status'),
]
