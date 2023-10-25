import os
import json
import pytz

from . mail import mail
from . models import *
from datetime import datetime
from django.conf import settings
from django.core.files.storage import default_storage
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.urls import reverse
from urllib.parse import urlencode
from dehaze import LWAED

# SAMPLE_FILES_PATH = [os.path.join(os.getcwd(), 'sample_videos', file) for file in os.listdir('sample_videos') if os.path.isfile(os.path.join('sample_videos', file))]
SAMPLE_FILES_PATH = os.listdir(os.path.join(settings.STATIC_ROOT, 'sample_videos'))
# dehazer = LWAED()


# Create your views here.
def index(request):
    return render(request, 'index.html')

def dehaze(request):
    return render(request, 'dehaze.html')

def upload(request):
    if request.method == "POST":
        # print(request)
        video_file = request.FILES['video_file']
        print(video_file)
        if video_file:
            input_file = default_storage.save(video_file.name, video_file)
            output_file = f"dehaze_{input_file}"

            input_file_path = os.path.join(settings.MEDIA_URL, input_file)
            output_file_path = os.path.join(settings.MEDIA_URL, output_file)
            input_file = os.path.join(settings.MEDIA_ROOT, input_file)
            output_file = os.path.join(settings.MEDIA_ROOT, output_file)

            dehazer = LWAED()
            dehazer.process_video(input_file, output_file)

            file_paths = {'input_file_path': input_file_path, 'output_file_path': output_file_path}

            file_paths_query_param = urlencode({'file_paths': json.dumps(file_paths)})
            url = reverse('results') + '?' + file_paths_query_param
            return redirect(url)
        
    return render(request, 'upload.html', {'file_paths': SAMPLE_FILES_PATH})

def upload_sample(request):
    if request.method == 'POST':
        video_file = request.POST['video_file']
        if video_file:
            output_file = f"dehaze_{video_file}"

            input_file_path = os.path.join(settings.STATIC_URL, 'sample_videos', video_file)
            output_file_path = os.path.join(settings.MEDIA_URL, output_file)
            input_file = os.path.join(settings.STATIC_ROOT, 'sample_videos', video_file)
            output_file = os.path.join(settings.MEDIA_ROOT, output_file)

            dehazer = LWAED()
            dehazer.process_video(input_file, output_file)

            file_paths = {'input_file_path': input_file_path, 'output_file_path': output_file_path}

            file_paths_query_param = urlencode({'file_paths': json.dumps(file_paths)})
            url = reverse('results') + '?' + file_paths_query_param
            return redirect(url)
        
    # return render(request, 'upload.html', {'file_paths': SAMPLE_FILES_PATH})


def results(request):
    if request.method == "GET":

        file_paths_param = request.GET.get('file_paths', None)

        if file_paths_param is not None:
            file_paths = json.loads(file_paths_param)
            input_file_path = file_paths.get('input_file_path', '')
            output_file_path = file_paths.get('output_file_path', '')
            return render(request, 'results.html', {'input_file_path': input_file_path, 'output_file_path': output_file_path})
        else:
            return HttpResponse("File paths not found or invalid.")  
        
def contact(request):
    if request.method == "POST":
        name = request.POST['name']
        email = request.POST['email']
        message = request.POST['msg']
        time = datetime.now(pytz.utc)

        SupportTicket.objects.create(name=name, email=email, message=message)
        Support_ID = SupportTicket.objects.get(name=name, email=email, message=message, created_at = time)
        print(Support_ID)
        print(Support_ID.ticket_no)
        support_mail = mail()
        support_mail.send_mail(name, email, message, Support_ID.ticket_no)
        
        print(name, email, message)
        return render(request, 'contact.html')

    return render(request, 'contact.html')

def about(request):
    return render(request, 'about.html')

def realtime(request):
    return render(request, 'realtime.html')
