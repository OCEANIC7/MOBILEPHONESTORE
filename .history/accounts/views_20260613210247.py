from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.models import User
from .models import Customer

def register(request):
    brands = get_brands()
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        phone = request.POST['phone']
        password = request.POST['password']
        confirm = request.POST['confirm_password']

        if password != confirm:
            return render(request, 'accounts/register.html', {
                'error': 'Passwords do not match.',
                'brands': brands
            })

        if User.objects.filter(username=username).exists():
            return render(request, 'accounts/register.html', {
                'error': 'Username already taken.',
                'brands': brands
            })

        user = User.objects.create_user(username=username, email=email, password=password)
        Customer.objects.create(User=user, PhoneNumber=phone)
        login(request, user)
        return redirect('home')

    return render(request, 'accounts/register.html', {'brands': brands})


def login_view(request):
    brands = get_brands()
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)

        if user:
            login(request, user)
            return redirect('home')
        else:
            return render(request, 'accounts/login.html', {
                'error': 'Invalid username or password.',
                'brands': brands
            })

    return render(request, 'accounts/login.html', {'brands': brands})


def logout_view(request):
    logout(request)
    return redirect('home')


# Helper to always pass brands to sidebar
def get_brands():
    from products.models import Brand
    return Brand.objects.all()