import json
import os
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.conf import settings
import assemblyai as aai
import pytube
from .models import TranscriptModel

# Create your views here.
def index(request):
    return render(request, 'index.html', {'user_info': 'index', })

@csrf_exempt
def generateBlog(request):
    if request.method == 'POST':
        try:
            data    =  json.loads(request.body)
            yt_link = data['link']
        except (KeyError, json.JSONDecodeError):
            return JsonResponse({'error': 'Invalid data sent'}, status=400)
        # get video title
        title = yt_title(yt_link)

        # get transcript
        transcription = get_transcript(yt_link)
        if not transcription:
            return JsonResponse({'error': 'Failed to get transcript'}, status = 400)

        # save generated transcript post to database
        new_transcript_post = TranscriptModel.objects.create(
            user                = request.user,
            youtube_title       = title,
            youtube_link        = yt_link,
            generated_content   = transcription
        )

        # return blog article as response
        return JsonResponse({'content': transcription})
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=401)

def yt_title(link):
    yt      = pytube.YouTube(link)
    title   = yt.title
    return title

def download_audio(link):
    yt      = pytube.YouTube(link)
    video   = yt.streams.filter(only_audio=True).first()
    output  = video.download(output_path = settings.MEDIA_ROOT)
    base, ext = os.path.splitext(output)
    new_file = base + '.mp3'
    os.rename(output, new_file)
    return new_file

def get_transcript(link):
    audio_file              = download_audio(link)
    aai.settings.api_key    = "your key"
    transcriber             = aai.Transcriber()
    transcript              = transcriber.transcribe(audio_file)
    return transcript.text

def transcript_list(request):
    transcript_post = TranscriptModel.objects.filter(user=request.user)
    return render(request, 'allblogs.html', {'transcript_posts': transcript_post})

def transcript_details(request, pk):
    transcript_details = TranscriptModel.objects.get(id=pk)
    if request.user == transcript_details.user:
        return render(request, 'transcriptdetails.html', {'transcript_details': transcript_details})
    else:
        return redirect('/')

def user_login(request):
    if request.method == 'POST':
        username        = request.POST['username']
        password        = request.POST['password']
        if username and password:
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return render(request, 'index.html', {'user_info': 'login'})
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
    return render(request, 'index.html', {'user_info': 'logout'})
