from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('apps.universities.urls')),
    path('accounts/', include('apps.accounts.urls')),
    path('ai/', include('apps.ai_assistant.urls')),
    path('dashboard/', include('apps.dashboard.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
