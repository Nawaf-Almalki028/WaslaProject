
from django.contrib import admin
from django.urls import path,include

urlpatterns = [
    path('admin/', admin.site.urls),
<<<<<<< HEAD
    path('dashboard/', include('dashboard.urls') )
] 
=======
    path('dashboard/', include('dashboard.urls')),
    path('accounts/', include('accounting.urls')),
]
>>>>>>> f38f101f4b65facf6d8f42d9effe3b39334fce32
