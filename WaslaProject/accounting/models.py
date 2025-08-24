from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import RegexValidator
from django.utils import timezone
import uuid

# Validator لرقم الهاتف
phone_regex = RegexValidator(
    regex=r'^\+?1?\d{9,15}$',
    message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed."
)


class User(AbstractUser):
    """
    نموذج المستخدم المخصص لـ WASLA
    يرث من AbstractUser ويضيف حقول إضافية
    """
    
    # خيارات نوع الحساب
    ACCOUNT_TYPE_CHOICES = [
        ('personal', _('Personal')),
        ('company', _('Company')),
    ]
    
    # === الحقول الأساسية ===
    email = models.EmailField(_('email address'), unique=True,help_text=_('Required. Enter a valid email address.'))
    
    username = models.CharField(_('username'),max_length=150,unique=True,help_text=_('Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.'),)
    
    # === معلومات إضافية ===
    phone_number = models.CharField(_('phone number'),validators=[phone_regex],max_length=17,blank=True,help_text=_('Enter phone number in international format'))
    
    account_type = models.CharField(_('account type'),max_length=10,choices=ACCOUNT_TYPE_CHOICES,default='personal',help_text=_('Select whether this is a personal or company account'))
    
    # === معلومات الملف الشخصي ===
    bio = models.TextField(_('bio'), max_length=500, blank=True,help_text=_('Brief description about yourself'))
    
    profile_image = models.ImageField(upload_to='profiles/%Y/%m/%d/',null=True,blank=True,help_text=_('Upload your profile picture'))
    
    # === معلومات التحقق ===
    is_verified = models.BooleanField(_('email verified'), default=False,help_text=_('Designates whether this user has verified their email.'))
    
    verification_token = models.UUIDField(default=uuid.uuid4, editable=False,help_text=_('Unique token for email verification'))
    
    # === معلومات الشركة (للحسابات التجارية) ===
    company_name = models.CharField(_('company name'), max_length=200, blank=True,help_text=_('Required for company accounts'))
    
    company_website = models.URLField(_('company website'), blank=True,help_text=_('Company website URL'))
    
    # === التواريخ والنشاط ===
    created_at = models.DateTimeField(auto_now_add=True,help_text=_('Date when the account was created'))
    
    updated_at = models.DateTimeField(auto_now=True,help_text=_('Date when the account was last updated'))
    
    last_activity = models.DateTimeField(default=timezone.now,help_text=_('Last time user was active on the platform'))
    
    # === إعدادات الإشعارات ===
    email_notifications = models.BooleanField(_('email notifications'),default=True,help_text=_('Receive email notifications about hackathons'))
    
    # تحديد الحقل المستخدم لتسجيل الدخول
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']
    
    class Meta:
        verbose_name = _('User')
        verbose_name_plural = _('Users')
        ordering = ['-created_at']
        indexes = [models.Index(fields=['email']),models.Index(fields=['username']),models.Index(fields=['created_at']),]
    
    def __str__(self):
        """عرض البريد الإلكتروني كاسم للمستخدم"""
        return self.email
    
    @property
    def full_name(self):
        """إرجاع الاسم الكامل أو اسم المستخدم"""
        full_name = f"{self.first_name} {self.last_name}".strip()
        return full_name or self.username
    
    @property
    def is_company_account(self):
        """التحقق من نوع الحساب"""
        return self.account_type == 'company'
    
    @property
    def participation_count(self):
        """عدد الهاكاثونات المشارك فيها"""
        return self.participations.count()
    
    @property
    def organized_count(self):
        """عدد الهاكاثونات المنظمة"""
        return self.organized_hackathons.count()
    
    def get_absolute_url(self):
        """الحصول على رابط الملف الشخصي"""
        from django.urls import reverse
        return reverse('accounts:user_profile', kwargs={'username': self.username})
    
    def update_last_activity(self):
        """تحديث آخر نشاط"""
        self.last_activity = timezone.now()
        self.save(update_fields=['last_activity'])
    
    def generate_new_verification_token(self):
        """توليد رمز تحقق جديد"""
        self.verification_token = uuid.uuid4()
        self.save(update_fields=['verification_token'])
        return self.verification_token