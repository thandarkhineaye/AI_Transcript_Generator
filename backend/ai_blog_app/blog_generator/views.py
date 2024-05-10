import json
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse

# Create your views here.
def index(request):
    return render(request, 'index.html')

@csrf_exempt
def generateBlog(request):
    if request.method == 'POST':
        try:
            data    =  json.loads(request.body)
            yt_link = data['link']
            return JsonResponse({'content': yt_link})
        except (KeyError, json.JSONDecodeError):
            return JsonResponse({'error': 'Invalid data sent'}, status=400)
            # get video title

            # get transcript

            # use OpenAI to generate the blog

            # save blog article to database

            # return blog article as response
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=401)

def user_login(request):
    if request.method == 'POST':
        username        = request.POST['username']
        password        = request.POST['password']
        if username and password:
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('/')
            else:
                error_messages = 'Invalid username or password'
                return render(request, 'login.html', {"error_message": error_messages})
        else:
            if username == '':
                error_messages = 'Please fill User Name'
            elif password == '':
                error_messages = 'Please fill Password'
            return render(request, 'login.html', {"error_message": error_messages})
    return render(request, 'login.html')

def user_signup(request):
    if request.method == 'POST':
        username        = request.POST['username']
        email           = request.POST['email']
        password        = request.POST['password']
        repeatPassword  = request.POST['repeatPassword']

        if username and email and password and repeatPassword:
            if password == repeatPassword:
                try:
                    user = User.objects.create_user(username=username, email=email, password=password)
                    user.save()
                    login(request, user)
                    return redirect('/')
                except:
                    error_messages = 'Error creating user account'
                    return render(request, 'signup.html', {"error_message": error_messages})
            else:
                error_messages  = 'Password do not match'
                return render(request, 'signup.html', {"error_message": error_messages})
        else:
            if username == '':
                error_messages = 'Please fill User Name'
            elif email == '':
                error_messages = 'Please fill Email'
            elif password == '':
                error_messages = 'Please fill Password'
            elif repeatPassword == '':
                error_messages = 'Please fill Retype Password'
            return render(request, 'signup.html', {"error_message": error_messages})
    return render(request, 'signup.html')

def user_logout(request):
    logout(request)
    return redirect('/')
