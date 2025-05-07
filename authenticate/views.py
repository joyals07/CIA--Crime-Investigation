from django.shortcuts import render,redirect,HttpResponse
from django.contrib.auth import authenticate,login
from django.contrib.auth.models import User
from django.contrib import messages

def index(request):
    return render(request,'index.html')

def loginn(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        # Authenticate user
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')  
        else:
            messages.error(request, 'Invalid username or password. Please try again.')
    return render(request, 'login.html')

def register(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        email=request.POST['email'] 
        # Create the user
        try:
            user = User.objects.create_user(username=username, password=password,email=email)
            user.save()
            messages.success(request, 'Registration successful! You can now log in.')
            return redirect('login')  
        except Exception as e:
            messages.error(request, f'Registration failed: {str(e)}')
    return render(request, 'register.html')

def home(request):
    return render(request, 'home.html')

