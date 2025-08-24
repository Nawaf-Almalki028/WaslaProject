# from django import forms
# from django.contrib.auth.forms import UserCreationForm
# from django.core.exceptions import ValidationError
# from django.contrib.auth import authenticate
# from .models import User


# class SignUpForm(UserCreationForm):
#     email = forms.EmailField(max_length=250)
#     username = forms.CharField(max_length=150)
#     phone_number = forms.CharField(required=False, max_length=20)
#     account_type = forms.ChoiceField(choices=User.ACCOUNT_TYPE_CHOICES)

#     class Meta:
#         model = User
#         fields = ('username', 'email', 'password1', 'password2', 'phone_number', 'account_type')

#     def clean_email(self):
#         email = self.cleaned_data.get('email')
#         if User.objects.filter(email=email).exists():
#             raise ValidationError('This email is already registered.')
#         return email

#     def clean_username(self):
#         username = self.cleaned_data.get('username')
#         if User.objects.filter(username=username).exists():
#             raise ValidationError('This username is already taken.')
#         return username


# class LoginForm(forms.Form):
#     identifier = forms.CharField(label='Email or Username', max_length=254)
#     password = forms.CharField(widget=forms.PasswordInput)

#     def clean(self):
#         cleaned = super().clean()
#         identifier = cleaned.get('identifier')
#         password = cleaned.get('password')

#         if not identifier or not password:
#             return cleaned

#         user = authenticate(username=identifier, password=password)

#         if not user and '@' in identifier:
#             try:
#                 u = User.objects.get(email=identifier)
#                 user = authenticate(username=u.username, password=password)
#             except User.DoesNotExist:
#                 user = None

#         if not user:
#             raise ValidationError('Invalid credentials.')

#         cleaned['user'] = user
#         return cleaned



# class UserProfileForm(forms.ModelForm):
#     first_name = forms.CharField(max_length=150)
#     last_name = forms.CharField(max_length=150)
#     bio = forms.CharField(widget=forms.Textarea, max_length=500)
#     phone_number = forms.CharField(max_length=20)
#     profile_image = forms.ImageField(required=False)
#     company_name = forms.CharField(max_length=255)
#     company_website = forms.URLField(required=False)
#     email_notifications = forms.BooleanField(required=False)

#     class Meta:
#         model = User
#         fields = [
#             'first_name', 'last_name', 'bio', 'phone_number',
#             'profile_image', 'company_name', 'company_website',
#             'email_notifications'
#         ]

#     def clean_profile_image(self):
#         img = self.cleaned_data.get('profile_image')
#         if img and img.size > 5 * 1024 * 1024:
#             raise ValidationError('Image file too large (max 5MB).')
#         return img



# class accountsettingsForm(forms.ModelForm):
#     email = forms.EmailField(max_length=250)
#     username = forms.CharField(max_length=150)
#     account_type = forms.ChoiceField(choices=User.ACCOUNT_TYPE_CHOICES)

#     class Meta:
#         model = User
#         fields = ['email', 'username', 'account_type']

#     def clean_email(self):
#         email = self.cleaned_data.get('email')
#         if User.objects.filter(email=email).exclude(pk=self.instance.pk).exists():
#             raise ValidationError('This email is already registered.')
#         return email

#     def clean_username(self):
#         username = self.cleaned_data.get('username')
#         if User.objects.filter(username=username).exclude(pk=self.instance.pk).exists():
#             raise ValidationError('This username is already taken.')
#         return username



# class DeleteAccountForm(forms.Form):
#     confirm_text = forms.CharField()
#     password = forms.CharField(widget=forms.PasswordInput)

#     def __init__(self, user, *args, **kwargs):
#         self.user = user
#         super().__init__(*args, **kwargs)

#     def clean_confirm_text(self):
#         text = self.cleaned_data.get('confirm_text')
#         if text != 'DELETE':
#             raise ValidationError('Please type DELETE to confirm.')
#         return text

#     def clean_password(self):
#         pwd = self.cleaned_data.get('password')
#         if not self.user.check_password(pwd):
#             raise ValidationError('Incorrect password.')
#         return pwd

#     #  مزايا اكثر لحقول إضافية
#     # email = forms.EmailField(
#     #     required=True,
#     #     label='Email Address',
#     #     widget=forms.EmailInput(attrs={
#     #         'class': 'form-control',
#     #         'placeholder': 'Email',
#     #         'required': 'required',
#     #         'autofocus': 'autofocus'
#     #     })
#     # )
    
# #     username = forms.CharField(
# #         max_length=150,
# #         required=True,
# #         label='Username',
# #         widget=forms.TextInput(attrs={
# #             'class': 'form-control',
# #             'placeholder': 'Username',
# #             'required': 'required'
# #         })
# #     )
    
# #     phone_number = forms.CharField(
# #         required=False,
# #         label='Phone',
# #         widget=forms.TextInput(attrs={
# #             'class': 'form-control',
# #             'placeholder': 'Phone Number (optional)',
# #             'pattern': '^\+?1?\d{9,15}$'
# #         })
# #     )
    
# #     account_type = forms.ChoiceField(
# #         choices=User.ACCOUNT_TYPE_CHOICES,
# #         initial='personal',
# #         label='Account Type',
# #         widget=forms.RadioSelect(attrs={
# #             'class': 'form-check-input'
# #         })
# #     )
    
# #     # حقول الشركة (تظهر فقط للحسابات التجارية)
# #     company_name = forms.CharField(
# #         required=False,
# #         label='Company',
# #         widget=forms.TextInput(attrs={
# #             'class': 'form-control',
# #             'placeholder': 'Company Name'
# #         })
# #     )
    
# #     company_website = forms.URLField(
# #         required=False,
# #         label='Company Website',
# #         widget=forms.URLInput(attrs={
# #             'class': 'form-control',
# #             'placeholder': 'https://company.com'
# #         })
# #     )
    
# #     # الموافقة على الشروط
# #     terms_accepted = forms.BooleanField(
# #         required=True,
# #         label='I agree to the Terms and Conditions',
# #         widget=forms.CheckboxInput(attrs={
# #             'class': 'form-check-input'
# #         })
# #     )
    
# #     class Meta:
# #         model = User
# #         fields = (
# #             'username', 'email', 'password1', 'password2',
# #             'phone_number', 'account_type', 'company_name', 
# #             'company_website'
# #         )
    
# #     def __init__(self, *args, **kwargs):
# #         super().__init__(*args, **kwargs)
        
# #         # تخصيص حقول كلمة المرور
# #         self.fields['password1'].widget.attrs.update({
# #             'class': 'form-control',
# #             'placeholder': 'Password',
# #             'required': 'required'
# #         })
# #         self.fields['password1'].label = 'Password'
        
# #         self.fields['password2'].widget.attrs.update({
# #             'class': 'form-control',
# #             'placeholder': 'Confirm Password',
# #             'required': 'required'
# #         })
# #         self.fields['password2'].label = 'Confirm Password'
    
# #     def clean_email(self):
# #         """التحقق من عدم وجود البريد الإلكتروني مسبقاً"""
# #         email = self.cleaned_data.get('email')
# #         if email and User.objects.filter(email=email).exists():
# #             raise ValidationError('This email is already registered.')
# #         return email
    
# #     def clean_username(self):
# #         """التحقق من عدم وجود اسم المستخدم مسبقاً"""
# #         username = self.cleaned_data.get('username')
# #         if username and User.objects.filter(username=username).exists():
# #             raise ValidationError('This username is already taken.')
# #         return username
    
# #     def clean(self):
# #         """التحقق من البيانات"""
# #         cleaned_data = super().clean()
# #         account_type = cleaned_data.get('account_type')
        
# #         # إذا كان حساب شركة، يجب إدخال اسم الشركة
# #         if account_type == 'company':
# #             company_name = cleaned_data.get('company_name')
# #             if not company_name:
# #                 self.add_error('company_name', 'Company name is required for company accounts.')
        
# #         return cleaned_data
    
# #     def save(self, commit=True):
# #         """حفظ المستخدم الجديد"""
# #         user = super().save(commit=False)
# #         user.email = self.cleaned_data['email']
        
# #         if commit:
# #             user.save()
        
# #         return user


# # class LoginForm(forms.Form):
# #     """
# #     نموذج تسجيل الدخول
# #     """
    
# #     email = forms.EmailField(
# #         label='Email or Username',
# #         widget=forms.EmailInput(attrs={
# #             'class': 'form-control',
# #             'placeholder': 'Email or Username',
# #             'autofocus': True,
# #             'required': 'required'
# #         })
# #     )
    
# #     password = forms.CharField(
# #         label='Password',
# #         widget=forms.PasswordInput(attrs={
# #             'class': 'form-control',
# #             'placeholder': 'Password',
# #             'required': 'required'
# #         })
# #     )
    
# #     remember_me = forms.BooleanField(
# #         required=False,
# #         label='Remember me',
# #         widget=forms.CheckboxInput(attrs={
# #             'class': 'form-check-input'
# #         })
# #     )
    
# #     def clean(self):
# #         """التحقق من بيانات تسجيل الدخول"""
# #         cleaned_data = super().clean()
# #         email = cleaned_data.get('email')
# #         password = cleaned_data.get('password')
        
# #         if email and password:
# #             # محاولة المصادقة
# #             user = authenticate(username=email, password=password)
# #             if not user:
# #                 raise ValidationError('Invalid email or password.')
            
# #             cleaned_data['user'] = user
        
# #         return cleaned_data


# # class UserProfileForm(forms.ModelForm):
# #     """
# #     نموذج تحديث الملف الشخصي
# #     """
    
# #     first_name = forms.CharField(
# #         required=False,
# #         label='First Name',
# #         widget=forms.TextInput(attrs={
# #             'class': 'form-control',
# #             'placeholder': 'First Name'
# #         })
# #     )
    
# #     last_name = forms.CharField(
# #         required=False,
# #         label='Last Name',
# #         widget=forms.TextInput(attrs={
# #             'class': 'form-control',
# #             'placeholder': 'Last Name'
# #         })
# #     )
    
# #     bio = forms.CharField(
# #         required=False,
# #         label='Bio',
# #         widget=forms.Textarea(attrs={
# #             'class': 'form-control',
# #             'rows': 4,
# #             'placeholder': 'Tell us about yourself...',
# #             'maxlength': 500
# #         })
# #     )
    
# #     phone_number = forms.CharField(
# #         required=False,
# #         label='Phone Number',
# #         widget=forms.TextInput(attrs={
# #             'class': 'form-control',
# #             'placeholder': 'Phone Number',
# #             'pattern': '^\+?1?\d{9,15}$'
# #         })
# #     )
    
# #     profile_image = forms.ImageField(
# #         required=False,
# #         label='Profile Picture',
# #         widget=forms.FileInput(attrs={
# #             'class': 'form-control',
# #             'accept': 'image/*'
# #         })
# #     )
    
# #     company_name = forms.CharField(
# #         required=False,
# #         label='Company Name',
# #         widget=forms.TextInput(attrs={
# #             'class': 'form-control',
# #             'placeholder': 'Company Name (for business accounts)'
# #         })
# #     )
    
# #     company_website = forms.URLField(
# #         required=False,
# #         label='Company Website',
# #         widget=forms.URLInput(attrs={
# #             'class': 'form-control',
# #             'placeholder': 'https://company.com'
# #         })
# #     )
    
# #     email_notifications = forms.BooleanField(
# #         required=False,
# #         label='Receive email notifications',
# #         widget=forms.CheckboxInput(attrs={
# #             'class': 'form-check-input'
# #         })
# #     )
    
# #     class Meta:
# #         model = User
# #         fields = [
# #             'first_name', 'last_name', 'bio', 'phone_number',
# #             'profile_image', 'company_name', 'company_website',
# #             'email_notifications'
# #         ]
    
# #     def __init__(self, *args, **kwargs):
# #         super().__init__(*args, **kwargs)
        
# #         # إخفاء حقول الشركة إذا كان الحساب شخصي
# #         if self.instance and self.instance.account_type == 'personal':
# #             self.fields.pop('company_name', None)
# #             self.fields.pop('company_website', None)
    
# #     def clean_profile_image(self):
# #         """التحقق من حجم الصورة"""
# #         image = self.cleaned_data.get('profile_image')
        
# #         if image:
# #             # التحقق من حجم الملف (5MB maximum)
# #             if image.size > 5 * 1024 * 1024:
# #                 raise ValidationError('Image file too large. Size should not exceed 5MB.')
        
# #         return image


# # class accountsettingsForm(forms.ModelForm):
# #     """
# #     نموذج إعدادات الحساب
# #     """
    
# #     email = forms.EmailField(
# #         label='Email Address',
# #         widget=forms.EmailInput(attrs={
# #             'class': 'form-control',
# #             'placeholder': 'Email'
# #         })
# #     )
    
# #     username = forms.CharField(
# #         label='Username',
# #         widget=forms.TextInput(attrs={
# #             'class': 'form-control',
# #             'placeholder': 'Username'
# #         })
# #     )
    
# #     account_type = forms.ChoiceField(
# #         choices=User.ACCOUNT_TYPE_CHOICES,
# #         label='Account Type',
# #         widget=forms.Select(attrs={
# #             'class': 'form-select'
# #         })
# #     )
    
# #     class Meta:
# #         model = User
# #         fields = ['email', 'username', 'account_type']
    
# #     def clean_email(self):
# #         """التحقق من عدم وجود البريد الإلكتروني لمستخدم آخر"""
# #         email = self.cleaned_data.get('email')
        
# #         if email:
# #             # استثناء المستخدم الحالي من الفحص
# #             existing = User.objects.filter(email=email).exclude(pk=self.instance.pk)
# #             if existing.exists():
# #                 raise ValidationError('This email is already registered.')
        
# #         return email
    
# #     def clean_username(self):
# #         """التحقق من عدم وجود اسم المستخدم لمستخدم آخر"""
# #         username = self.cleaned_data.get('username')
        
# #         if username:
# #             # استثناء المستخدم الحالي من الفحص
# #             existing = User.objects.filter(username=username).exclude(pk=self.instance.pk)
# #             if existing.exists():
# #                 raise ValidationError('This username is already taken.')
        
# #         return username


# # class DeleteAccountForm(forms.Form):
# #     """
# #     نموذج حذف الحساب
# #     """
    
# #     confirm_text = forms.CharField(
# #         label='Type "DELETE" to confirm',
# #         widget=forms.TextInput(attrs={
# #             'class': 'form-control',
# #             'placeholder': 'Type DELETE to confirm'
# #         })
# #     )
    
# #     password = forms.CharField(
# #         label='Enter your password',
# #         widget=forms.PasswordInput(attrs={
# #             'class': 'form-control',
# #             'placeholder': 'Password'
# #         })
# #     )
    
# #     def __init__(self, user, *args, **kwargs):
# #         self.user = user
# #         super().__init__(*args, **kwargs)
    
# #     def clean_confirm_text(self):
# #         """التحقق من نص التأكيد"""
# #         confirm_text = self.cleaned_data.get('confirm_text')
        
# #         if confirm_text != 'DELETE':
# #             raise ValidationError('Please type DELETE to confirm.')
        
# #         return confirm_text
    
# #     def clean_password(self):
# #         """التحقق من كلمة المرور"""
# #         password = self.cleaned_data.get('password')
        
# #         if not self.user.check_password(password):
# #             raise ValidationError('Incorrect password.')
        
# #         return password