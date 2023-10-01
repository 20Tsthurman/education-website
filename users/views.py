from django.contrib.auth.decorators import login_required
from .forms import UserRegistrationForm
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login, logout
from django.shortcuts import render, redirect
from django.contrib.auth.views import PasswordChangeView,PasswordChangeDoneView
from django.urls import reverse_lazy
from django.contrib import messages
from django.contrib.auth import login as auth_login
from django.contrib.auth.models import Group
from django.contrib.auth.forms import UserCreationForm

@login_required
def dashboard(request):
    return render(request, 'dashboard.html')

def homepage(request):
    return render(request, 'homepage.html')

def about(request):
    return render(request, 'about.html')

def contact(request):
    return render(request, 'contact.html')



def register(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            auth_login(request, user)  # Log the user in after registration

            # Assign the user to the "Default" group
            default_group, _ = Group.objects.get_or_create(name='Default')
            user.groups.add(default_group)

            return redirect('dashboard')  # Redirect to the dashboard or any other desired page
    else:
        form = UserRegistrationForm()
        print(form.errors) 
    return render(request, 'registration/register.html', {'form': form})



def user_login(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            auth_login(request, user)  # Log the user in after successful login
            return redirect('dashboard')  # Redirect to the dashboard or any other desired page
    else:
        form = AuthenticationForm()
        print(form.errors) 
    return render(request, 'registration/login.html', {'form': form})


def user_logout(request):
    logout(request)  # Log the user out
    return redirect('login')  # Redirect to the login page

# users/views.py

from django.contrib.auth.decorators import login_required
from .forms import UserRegistrationForm

@login_required
def account_settings(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
    else:
        form = UserRegistrationForm(instance=request.user)
    return render(request, 'account_settings.html', {'form': form})

class CustomPasswordChangeView(PasswordChangeView):
    template_name = 'password_change.html'  # Replace with your desired template
    success_url = reverse_lazy('password_change_done')  # URL to redirect after a successful password change

    # Customize the view as needed
    def form_valid(self, form):
        messages.success(self.request, 'Your password has been successfully changed.')  # Display a success message
        return super().form_valid(form)
    
class CustomPasswordChangeDoneView(PasswordChangeDoneView):
    template_name = 'password_change_done.html'  # Replace with your desired template

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Add any additional context data you want to pass to the template
        return context