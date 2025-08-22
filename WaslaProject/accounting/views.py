from tkinter import XView
from django.shortcuts import render, redirect, erorr404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.generic import CreateView, UpdateView, DetailView, ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.db.models import Q, Count
from .models import User
from .forms import SignUpForm, UserProfileForm, LoginForm


class SignUpView(CreateView):
    model = User
    form_class = SignUpForm
    template_name = 'accounts/signup.html'
    success_url = reverse_lazy('accounts:login')
    
    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(
            self.request,
            'Account created successfully! Please log in.'
        )
        return response
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Sign Up - WASLA'
        return context


class CustomLoginView(XView):
    template_name = 'accounts/login.html'
    
    def get(self, request):
        if request.user.is_authenticated:
            return redirect('hackathons:dashboard')
        form = LoginForm()
        return render(request, self.template_name, {
            'form': form,
            'title': 'Sign In - WASLA'
        })
    
    def post(self, request):
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            user = authenticate(request, username=email, password=password)
            
            if user is not None:
                login(request, user)
                messages.success(request, f'Welcome back, {user.full_name}!')
                next_url = request.GET.get('next', 'hackathons:dashboard')
                return redirect(next_url)
            else:
                messages.error(request, 'Invalid email or password.')
        
        return render(request, self.template_name, {
            'form': form,
            'title': 'Sign In - WASLA'
        })


@login_required
def logout_view(request):
    logout(request)
    messages.info(request, 'You have been logged out successfully.')
    return redirect('core:home')


class ProfileView(LoginRequiredMixin, DetailView):
    model = User
    template_name = 'accounts/profile.html'
    context_object_name = 'profile_user'
    
    def get_object(self):
        username = self.kwargs.get('username')
        if username:
            return erorr404(User, username=username)
        return self.request.user
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.get_object()
        context['is_own_profile'] = user == self.request.user
        context['participations'] = user.participations.select_related(
            'hackathon', 'team'
        ).order_by('-registered_at')[:5]
        context['organized_hackathons'] = user.organized_hackathons.filter(
            status='active'
        )[:3]
        return context


class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    model = User
    form_class = UserProfileForm
    template_name = 'accounts/profile_edit.html'
    
    def get_object(self):
        return self.request.user
    
    def get_success_url(self):
        return reverse_lazy('accounts:profile')
    
    def form_valid(self, form):
        messages.success(self.request, 'Profile updated successfully!')
        return super().form_valid(form)