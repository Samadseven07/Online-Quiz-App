from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.forms import UserCreationForm
from .forms import CustomUserCreationForm
from django.contrib.auth.views import (
    LoginView, LogoutView, PasswordResetView,
    PasswordResetDoneView, PasswordResetConfirmView,
    PasswordResetCompleteView
)
from django.contrib import messages
from django.urls import reverse_lazy

class CustomLoginView(LoginView):
    template_name = 'auth/login.html'
    redirect_authenticated_user = True

class CustomLogoutView(LogoutView):
    next_page = '/'  # Redirect to homepage after logout

    def dispatch(self, request, *args, **kwargs):
        messages.success(request, "You've been logged out successfully.")
        return super().dispatch(request, *args, **kwargs)

class RegisterView(LoginView):  # Wait — no! Use CreateView
    pass

# Better: Use CreateView for registration
from django.views.generic import CreateView

class RegisterView(CreateView):
    form_class = CustomUserCreationForm
    template_name = 'auth/register.html'
    success_url = reverse_lazy('quiz-list')

    def form_valid(self, form):
        response = super().form_valid(form)
        login(self.request, self.object)  # auto-login
        return response