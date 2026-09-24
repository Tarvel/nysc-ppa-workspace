from django.urls import path
from . import views

app_name = 'outreach'

urlpatterns = [
    path('', views.outreach_list_view, name='list'),
    path('prepare/<int:org_id>/', views.prepare_outreach_view, name='prepare'),
    path('<int:pk>/update/', views.update_outreach_status_view, name='update_status'),
]
