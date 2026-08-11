from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect

def staff_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None and hasattr(user, 'staff_profile'):
            login(request, user)
            return redirect('staff_dashboard') # placeholder - built in Sprint 5
        return render(request, 'staff/login.html', {'error': 'Invalid credentials'})
    return render(request, 'staff/login.html')

@login_required
def staff_logout(request):
    logout(request)
    return redirect('staff_login')
