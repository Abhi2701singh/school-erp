from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from accounts.forms import LoginForm, UserForm
from schools.models import School

def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f"Welcome back, {user.get_full_name() or user.username}!")
            return redirect('dashboard')
        else:
            messages.error(request, "Invalid username or password.")
    else:
        form = LoginForm()

    return render(request, 'accounts/login.html', {'form': form})


def logout_view(request):
    logout(request)
    messages.info(request, "You have been logged out.")
    return redirect('login')


@login_required
def profile_view(request):
    user = request.user
    if request.method == 'POST':
        form = UserForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated successfully!")
            return redirect('profile')
    else:
        form = UserForm(instance=user)

    return render(request, 'accounts/profile.html', {'form': form, 'user_obj': user})


@login_required
def switch_school_view(request, school_id):
    if not request.user.is_super_admin():
        messages.error(request, "Permission denied.")
        return redirect('dashboard')

    if school_id == 0:
        request.session['active_school_id'] = None
        messages.info(request, "Switched to All Schools view.")
    else:
        school = get_object_or_404(School, pk=school_id)
        request.session['active_school_id'] = school.id
        messages.success(request, f"Switched context to {school.name}.")

    return redirect('dashboard')
