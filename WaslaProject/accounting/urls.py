from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = 'accounts'

urlpatterns = [
    # Authentication - صفحة واحدة مدمجة
    path('auth/', views.AuthView.as_view(), name='auth'),
    path('auth/<str:tab>/', views.AuthView.as_view(), name='auth_tab'),
    path('logout/', views.logout_view, name='logout'),
    
    # Profile - صفحة واحدة مدمجة للملف الشخصي والإعدادات
    path('profile/', views.ProfileView.as_view(), name='profile'),
    path('profile/<str:username>/', views.ProfileView.as_view(), name='user_profile'),
    
    # Email Verification
    path('verify/<str:token>/', views.verify_email, name='verify_email'),
    path('resend-verification/', views.resend_verification, name='resend_verification'),
    
    # Password Reset - استخدام صفحة الرسائل العامة
    path('password-reset/', views.password_reset, name='password_reset'),
    path('reset/<uidb64>/<token>/', views.password_reset_confirm, name='password_reset_confirm'),
    
    # AJAX endpoints
    path('api/check-username/', views.check_username, name='check_username'),
    path('api/check-email/', views.check_email, name='check_email'),
]