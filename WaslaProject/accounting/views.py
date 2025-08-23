from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.views import View
from django.views.generic import CreateView, UpdateView, DetailView
from django.urls import reverse_lazy, reverse
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.utils import timezone
from django.http import HttpResponseRedirect, JsonResponse
from django.db.models import Q, Count
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
import json
from .models import User
from .forms import SignUpForm, LoginForm, UserProfileForm, AccountSettingsForm,DeleteAccountForm



class AuthView(View):
    """
    View موحد للمصادقة - يجمع Login, Signup, Password Reset
    """
    template_name = 'accounts/auth.html'
    
    def get(self, request, tab='login'):
        """عرض صفحة المصادقة مع التبويب المناسب"""
        if request.user.is_authenticated and tab != 'reset':
            return redirect('hackathons:dashboard')
        
        context = {
            'view_type': tab,
            'title': self._get_page_title(tab),
            'next': request.GET.get('next', ''),
        }
        
        # إضافة النموذج المناسب حسب التبويب
        if tab == 'login':
            context['login_form'] = LoginForm()
        elif tab == 'signup':
            context['signup_form'] = SignUpForm()
        
        return render(request, self.template_name, context)
    
    def post(self, request, tab='login'):
        """معالجة بيانات النماذج"""
        action = request.POST.get('action', tab)
        
        if action == 'login':
            return self._handle_login(request)
        elif action == 'signup':
            return self._handle_signup(request)
        elif action == 'reset':
            return self._handle_password_reset(request)
        
        return redirect('accounts:auth')
    
    def _handle_login(self, request):
        """معالجة تسجيل الدخول"""
        form = LoginForm(request.POST)
        
        if form.is_valid():
            identifier = form.cleaned_data.get('identifier')
            password = form.cleaned_data.get('password')
            
            # محاولة المصادقة
            user = self._authenticate_user(request, identifier, password)
            
            if user:
                # التحقق من تفعيل البريد
                if not user.is_verified:
                    messages.warning(request, 'Please verify your email first.')
                    return redirect('accounts:resend_verification')
                
                # تسجيل الدخول
                login(request, user)
                user.update_last_activity()
                
                messages.success(request, f'Welcome back, {user.full_name}!')
                next_url = request.GET.get('next', 'hackathons:dashboard')
                return redirect(next_url)
            else:
                messages.error(request, 'Invalid credentials.')
        
        return self.get(request, tab='login')
    
    def _handle_signup(self, request):
        """معالجة التسجيل"""
        form = SignUpForm(request.POST)
        
        if form.is_valid():
            user = form.save()
            self._send_verification_email(user, request)
            
            messages.success(
                request,
                'Account created! Please check your email to verify.'
            )
            return redirect('accounts:auth_tab', tab='login')
        
        context = {
            'view_type': 'signup',
            'signup_form': form,
            'title': 'Sign Up - WASLA'
        }
        return render(request, self.template_name, context)
    
    def _handle_password_reset(self, request):
        """معالجة إعادة تعيين كلمة المرور"""
        email = request.POST.get('email')
        
        if email:
            try:
                user = User.objects.get(email=email)
                self._send_password_reset_email(user, request)
                
                return render(request, 'accounts/messages.html', {
                    'title': 'Check Your Email',
                    'message': 'Password reset link has been sent to your email.',
                    'message_type': 'success',
                    'action_url': reverse('accounts:auth'),
                    'action_text': 'Back to Login'
                })
            except User.DoesNotExist:
                messages.error(request, 'No account found with this email.')
        
        return self.get(request, tab='reset')
    
    def _authenticate_user(self, request, identifier, password):
        """محاولة المصادقة بالبريد أو اسم المستخدم"""
        # محاولة بالبريد أولاً
        user = authenticate(request, username=identifier, password=password)
        
        # إذا فشلت، محاولة باسم المستخدم
        if not user and '@' not in identifier:
            try:
                user_obj = User.objects.get(username=identifier)
                user = authenticate(request, username=user_obj.email, password=password)
            except User.DoesNotExist:
                pass
        
        return user
    
    def _send_verification_email(self, user, request):
        """إرسال بريد التحقق"""
        verification_url = request.build_absolute_uri(
            reverse('accounts:verify_email', kwargs={'token': user.verification_token})
        )
        
        html_message = render_to_string('accounts/email/verify_email.html', {
            'user': user,
            'verification_url': verification_url,
        })
        
        send_mail(
            subject='Verify your WASLA account',
            message=strip_tags(html_message),
            from_email='noreply@wasla.com',
            recipient_list=[user.email],
            html_message=html_message,
            fail_silently=False
        )
    
    def _send_password_reset_email(self, user, request):
        """إرسال بريد إعادة تعيين كلمة المرور"""
        token = default_token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        
        reset_url = request.build_absolute_uri(
            reverse('accounts:password_reset_confirm', kwargs={
                'uidb64': uid,
                'token': token
            })
        )
        
        html_message = render_to_string('accounts/email/password_reset_email.html', {
            'user': user,
            'reset_url': reset_url,
        })
        
        send_mail(
            subject='Reset your WASLA password',
            message=strip_tags(html_message),
            from_email='noreply@wasla.com',
            recipient_list=[user.email],
            html_message=html_message,
            fail_silently=False
        )
    
    def _get_page_title(self, tab):
        """الحصول على عنوان الصفحة"""
        titles = {
            'login': 'Sign In - WASLA',
            'signup': 'Sign Up - WASLA',
            'reset': 'Reset Password - WASLA'
        }
        return titles.get(tab, 'WASLA')


class ProfileView(LoginRequiredMixin, View):
    """
    View موحد للملف الشخصي - يجمع Profile, Edit, Settings, Security
    """
    template_name = 'accounts/profile.html'
    
    def get(self, request, username=None):
        """عرض الملف الشخصي"""
        # الحصول على المستخدم
        if username:
            profile_user = get_object_or_404(User, username=username)
        else:
            profile_user = request.user
        
        context = {
            'profile_user': profile_user,
            'is_own_profile': profile_user == request.user,
            'title': f'{profile_user.full_name} - Profile',
            'participations': self._get_participations(profile_user),
            'stats': self._get_user_stats(profile_user),
        }
        
        # إضافة النماذج إذا كان الملف الشخصي خاص بالمستخدم
        if context['is_own_profile']:
            context['profile_form'] = UserProfileForm(instance=profile_user)
            context['settings_form'] = AccountSettingsForm(instance=profile_user)
            context['delete_form'] = DeleteAccountForm(user=profile_user)
        
        return render(request, self.template_name, context)
    
    @require_http_methods(["POST"])
    def post(self, request, username=None):
        """معالجة تحديثات الملف الشخصي"""
        if username and username != request.user.username:
            messages.error(request, 'You can only edit your own profile.')
            return redirect('accounts:profile')
        
        action = request.POST.get('action')
        
        if action == 'edit_profile':
            return self._handle_profile_edit(request)
        elif action == 'update_settings':
            return self._handle_settings_update(request)
        elif action == 'change_password':
            return self._handle_password_change(request)
        elif action == 'delete_account':
            return self._handle_account_deletion(request)
        
        return redirect('accounts:profile')
    
    def _handle_profile_edit(self, request):
        """معالجة تعديل الملف الشخصي"""
        form = UserProfileForm(
            request.POST, 
            request.FILES, 
            instance=request.user
        )
        
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
        else:
            messages.error(request, 'Please correct the errors below.')
        
        return redirect('accounts:profile')
    
    def _handle_settings_update(self, request):
        """معالجة تحديث الإعدادات"""
        form = AccountSettingsForm(request.POST, instance=request.user)
        
        if form.is_valid():
            # التحقق من تغيير البريد الإلكتروني
            if 'email' in form.changed_data:
                form.instance.is_verified = False
                form.instance.generate_new_verification_token()
                # إرسال بريد تحقق جديد
                AuthView()._send_verification_email(form.instance, request)
                messages.warning(request, 'Please verify your new email address.')
            
            form.save()
            messages.success(request, 'Settings updated successfully!')
        else:
            messages.error(request, 'Please correct the errors below.')
        
        return redirect('accounts:profile')
    
    def _handle_password_change(self, request):
        """معالجة تغيير كلمة المرور"""
        old_password = request.POST.get('old_password')
        new_password1 = request.POST.get('new_password1')
        new_password2 = request.POST.get('new_password2')
        
        # التحقق من كلمة المرور القديمة
        if not request.user.check_password(old_password):
            messages.error(request, 'Current password is incorrect.')
            return redirect('accounts:profile')
        
        # التحقق من تطابق كلمات المرور الجديدة
        if new_password1 != new_password2:
            messages.error(request, 'New passwords do not match.')
            return redirect('accounts:profile')
        
        # التحقق من قوة كلمة المرور
        if len(new_password1) < 8:
            messages.error(request, 'Password must be at least 8 characters.')
            return redirect('accounts:profile')
        
        # تغيير كلمة المرور
        request.user.set_password(new_password1)
        request.user.save()
        
        # إعادة تسجيل الدخول
        login(request, request.user)
        messages.success(request, 'Password changed successfully!')
        
        return redirect('accounts:profile')
    
    def _handle_account_deletion(self, request):
        """معالجة حذف الحساب"""
        form = DeleteAccountForm(user=request.user, data=request.POST)
        
        if form.is_valid():
            user = request.user
            logout(request)
            user.delete()
            
            messages.success(request, 'Your account has been deleted.')
            return redirect('core:home')
        
        messages.error(request, 'Invalid confirmation. Please try again.')
        return redirect('accounts:profile')
    
    def _get_participations(self, user):
        """الحصول على آخر المشاركات"""
        return user.participations.select_related(
            'hackathon', 'team'
        ).order_by('-registered_at')[:5]
    
    def _get_user_stats(self, user):
        """الحصول على إحصائيات المستخدم"""
        return {
            'participations': user.participation_count,
            'organized': user.organized_count,
            'teams': user.participations.exclude(team=None).count(),
        }


@login_required
def logout_view(request):
    """تسجيل الخروج"""
    logout(request)
    messages.info(request, 'You have been logged out successfully.')
    return redirect('core:home')


def verify_email(request, token):
    """التحقق من البريد الإلكتروني"""
    try:
        user = User.objects.get(verification_token=token)
        
        if not user.is_verified:
            user.is_verified = True
            user.save()
            login(request, user)
            messages.success(request, 'Email verified successfully!')
        else:
            messages.info(request, 'Email already verified.')
        
        return redirect('hackathons:dashboard')
        
    except User.DoesNotExist:
        return render(request, 'accounts/messages.html', {
            'title': 'Invalid Link',
            'message': 'This verification link is invalid or has expired.',
            'message_type': 'error',
            'action_url': reverse('accounts:auth'),
            'action_text': 'Go to Login'
        })


@login_required
def resend_verification(request):
    """إعادة إرسال بريد التحقق"""
    if request.user.is_verified:
        messages.info(request, 'Your email is already verified.')
        return redirect('hackathons:dashboard')
    
    request.user.generate_new_verification_token()
    AuthView()._send_verification_email(request.user, request)
    
    messages.success(request, 'Verification email sent!')
    return redirect('accounts:profile')


def password_reset(request):
    """إعادة تعيين كلمة المرور"""
    if request.method == 'POST':
        return AuthView().post(request, tab='reset')
    return AuthView().get(request, tab='reset')


def password_reset_confirm(request, uidb64, token):
    """تأكيد إعادة تعيين كلمة المرور"""
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    
    if user and default_token_generator.check_token(user, token):
        if request.method == 'POST':
            new_password = request.POST.get('new_password1')
            confirm_password = request.POST.get('new_password2')
            
            if new_password == confirm_password and len(new_password) >= 8:
                user.set_password(new_password)
                user.save()
                
                return render(request, 'accounts/messages.html', {
                    'title': 'Password Reset Complete',
                    'message': 'Your password has been reset successfully.',
                    'message_type': 'success',
                    'action_url': reverse('accounts:auth'),
                    'action_text': 'Go to Login'
                })
            else:
                messages.error(request, 'Passwords do not match or are too short.')
        
        return render(request, 'accounts/password_reset_confirm.html', {
            'validlink': True,
            'uidb64': uidb64,
            'token': token
        })
    
    return render(request, 'accounts/messages.html', {
        'title': 'Invalid Link',
        'message': 'This password reset link is invalid or has expired.',
        'message_type': 'error',
        'action_url': reverse('accounts:auth_tab', kwargs={'tab': 'reset'}),
        'action_text': 'Request New Link'
    })


# === AJAX Views ===

@login_required
@require_http_methods(["GET"])
def check_username(request):
    """التحقق من توفر اسم المستخدم"""
    username = request.GET.get('username', '')
    
    if username:
        exists = User.objects.filter(username=username).exclude(
            pk=request.user.pk
        ).exists()
        
        return JsonResponse({
            'available': not exists,
            'message': 'Username taken' if exists else 'Username available'
        })
    
    return JsonResponse({
        'available': False,
        'message': 'Username required'
    })


@login_required
@require_http_methods(["GET"])
def check_email(request):
    """التحقق من توفر البريد الإلكتروني"""
    email = request.GET.get('email', '')
    
    if email:
        exists = User.objects.filter(email=email).exclude(
            pk=request.user.pk
        ).exists()
        
        return JsonResponse({
            'available': not exists,
            'message': 'Email already registered' if exists else 'Email available'
        })
    
    return JsonResponse({
        'available': False,
        'message': 'Email required'
    })