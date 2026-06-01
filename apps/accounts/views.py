from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import RegisterForm, LoginForm, ProfileForm
from apps.universities.models import FavoriteUniversity

def register_view(request):
    if request.user.is_authenticated:
        return redirect('home')
    form = RegisterForm(request.POST or None)
    if form.is_valid():
        user = form.save()
        login(request, user)
        messages.success(request, f"Welcome, {user.first_name or user.username}! 🎉")
        return redirect('home')
    return render(request, 'accounts/register.html', {'form': form})

def login_view(request):
    if request.user.is_authenticated:
        return redirect('home')
    form = LoginForm(request, data=request.POST or None)
    if request.method == 'POST' and form.is_valid():
        login(request, form.get_user())
        messages.success(request, "Welcome back! 👋")
        return redirect(request.GET.get('next', 'home'))
    return render(request, 'accounts/login.html', {'form': form})

def logout_view(request):
    logout(request)
    messages.info(request, "You have been logged out.")
    return redirect('login')

@login_required
def profile_view(request):
    profile = request.user.profile
    form = ProfileForm(request.POST or None, request.FILES or None, instance=profile)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, "Profile updated successfully!")
        return redirect('profile')
    favorites = FavoriteUniversity.objects.filter(user=request.user).select_related('university')
    return render(request, 'accounts/profile.html', {'form': form, 'favorites': favorites})
