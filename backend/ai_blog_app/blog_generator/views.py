import json
import os
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.conf import settings
from django.contrib.auth.models import AnonymousUser
from django.http import HttpResponse
import logging
import assemblyai as aai
import pytube
from .models import TranscriptModel
from credentials.key import assembly_api_key
logger = logging.getLogger(__name__)


def index(request):
    """
    Direct to main index page

    Parameters  : request
    Returns     : render to index.html
    """
    return render(request, 'index.html')

@csrf_exempt
def generateTranscript(request):
    """
    Generate Transcript from given Youtube video link

    Parameters  : None
    Returns     : JsonResponse
    """
    if request.method == 'POST':
        try:
            data        = json.loads(request.body)
            yt_link     = data['link']
            logger.info(f"[generateBlog] youtube link -> {yt_link}")
        except (KeyError, json.JSONDecodeError):
            logger.error(f"[generateBlog] Invalid data sent")
            return JsonResponse({'error': 'Invalid data sent'}, status=400)

        # get video title
        title           = yt_title(yt_link)
        logger.info(f"[generateBlog] youtube video title -> {title}")

        # get transcript
        transcription   = get_transcript(yt_link)
        if not transcription:
            logger.error(f"[generateBlog] Failed to get transcript -> {title}")
            return JsonResponse({'error': 'Failed to get transcript'}, status = 400)

        # save generated transcript post to database
        logger.info(f"[generateBlog] video request.user -> {request.user}")
        if not isinstance(request.user, AnonymousUser):
            new_transcript_post     = TranscriptModel.objects.create(
                user                = request.user,
                youtube_title       = title,
                youtube_link        = yt_link,
                generated_content   = transcription
            )
        # return blog article as response
        logger.info(f"[generateBlog] Finish create transcription")
        return JsonResponse({'content': transcription})
    else:
        logger.warning(f"[generateBlog] Invalid request method")
        return JsonResponse({'error': 'Invalid request method'}, status=401)

def deletePost(request, pk):
    """
    Delete Transcript Post when delete button clicked

    Parameters  : request
                  pk which id for deleted post
    Returns     : JsonResponse or redirect
    """
    if request.method == 'POST':
        # delete transcript post to database
        logger.info(f"[deletePost] video request.user -> {request.user}")
        if not isinstance(request.user, AnonymousUser):
            TranscriptModel.objects.filter(id=pk).delete()
        # return deleted pk as response
        logger.info(f"[deletePost] Finish delete transcription")
        transcript_post = TranscriptModel.objects.filter(user=request.user)
        return redirect('/transcript-list', {'transcript_posts': transcript_post})
    else:
        logger.warning(f"[deletePost] Invalid delete request method")
        return JsonResponse({'error': 'Invalid delete request method'}, status=401)

def exportText(request, pk):
    """
    Export Transcript text file when Export Text button clicked

    Parameters  : request
                  pk which id for export text file
    Returns     : JsonResponse or redirect
    """
    if request.method == 'POST':
        # delete transcript post to database
        logger.info(f"[exportText] video request.user -> {request.user}")
        transcript_details = TranscriptModel.objects.get(id=pk)

        if not os.path.exists(settings.TEXT_ROOT):
            os.makedirs(settings.TEXT_ROOT)
        # Define the file path for the Text file
        file_path = os.path.join(settings.TEXT_ROOT, f'exported_data.txt')

        # Create and open the text file in write mode
        with open(file_path, 'w') as text_file:
            # Write the content to the text file
            text_file.write(f"Youtube Title: {transcript_details.youtube_title}\n")
            text_file.write(f"Content: {transcript_details.generated_content}")

        transcript_post = TranscriptModel.objects.filter(user=request.user)
        return redirect('/transcript-list', {'transcript_posts': transcript_post})
    else:
        logger.warning(f"[exportText] Invalid delete request method")
        return JsonResponse({'error': 'Invalid delete request method'}, status=401)

def yt_title(link):
    """
    Get Youtube link title

    Parameters  : youtube link
    Returns     : youtube video title
    """
    yt      = pytube.YouTube(link)
    title   = yt.title
    return title

def download_audio(link):
    """
    download audio file from youtube link

    Parameters  : youtube link
    Returns     : audio file
    """
    yt      = pytube.YouTube(link)
    video   = yt.streams.filter(only_audio=True).first()
    if not os.path.exists(settings.MEDIA_ROOT):
        os.makedirs(settings.MEDIA_ROOT)
        logger.info(f"[download_audio] Media Folder not exists, so created")
    else:
        # List all files in the folder
        file_list = os.listdir(settings.MEDIA_ROOT)
        # Iterate over the files and delete them
        for file_name in file_list:
            logger.info(f"[download_audio] Media filename {file_name}")
            file_path = os.path.join(settings.MEDIA_ROOT, file_name)
            if os.path.isfile(file_path):
                os.remove(file_path)
                logger.info(f"[download_audio] Deleted {file_path}")
        logger.info(f"[download_audio] Media Folder already exists and cleared")

    output  = video.download(output_path = settings.MEDIA_ROOT)
    base, ext = os.path.splitext(output)
    new_file = base + '.mp3'
    os.rename(output, new_file)
    return new_file

def get_transcript(link):
    """
    generated transcript from  youtube link with assemblyai API.
    need to replace valid assemblyai API key to "your key".

    Parameters  : youtube link
    Returns     : transcript text
    """
    audio_file              = download_audio(link)
    aai.settings.api_key    = assembly_api_key
    transcriber             = aai.Transcriber()
    transcript              = transcriber.transcribe(audio_file)
    return transcript.text

def transcript_list(request):
    """
    Display All transcript list page.

    Parameters  : youtube link
    Returns     : render to transcript list page or redirect to home page
    """
    transcript_post = TranscriptModel.objects.filter(user=request.user)
    return render(request, 'allblogs.html', {'transcript_posts': transcript_post})

def transcript_details(request, pk):
    """
    Display Full Transcript text.

    Parameters  : request
                  pk which id for full display text file
    Returns     : JsonResponse or redirect
    """
    transcript_details = TranscriptModel.objects.get(id=pk)
    if request.user == transcript_details.user:
        return render(request, 'transcriptdetails.html', {'transcript_details': transcript_details})
    else:
        return redirect('/')

def user_login(request):
    """
    User Login

    Parameters  : request
    Returns     : render to log in page
    """
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
    """
    User Sign Up

    Parameters  : request
    Returns     : render to Sign Up page
    """
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
    """
    User Log Out

    Parameters  : request
    Returns     : redirect back to index page.
    """
    logout(request)
    return redirect('/')
