from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('core.urls')),
    path('accounts/', include('accounts.urls')),
    path('organizations/', include('organizations.urls')),
    path('contacts/', include('contacts.urls')),
    path('outreach/', include('outreach.urls')),
]
