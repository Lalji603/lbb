from django.shortcuts import render, redirect
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages

def custom_logout(request):
    if request.method == 'POST':
        logout(request)
        messages.success(request, 'You have been successfully logged out.')
        return redirect('login')
    else:
        # For GET requests, just show the logout page
        return render(request, 'bloodbank/logout.html')

from django.contrib.auth.views import LoginView

def custom_login(request, **kwargs):
    # Forcefully log out any authenticated user who navigates to the login page
    if request.user.is_authenticated:
        logout(request)
    return LoginView.as_view(template_name='bloodbank/login_modern.html')(request, **kwargs)
