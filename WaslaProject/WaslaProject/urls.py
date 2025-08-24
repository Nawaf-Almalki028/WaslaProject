
from django.contrib import admin
from django.urls import include, path
from django.conf.urls.static import static
from WaslaProject import settings

urlpatterns = [
    path('admin/', admin.site.urls),
    path('dashboard/', include('dashboard.urls')),
    path('accounts/'), include('accounts.url')),
    path('', include('main.urls')),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

