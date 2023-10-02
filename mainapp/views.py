import os
import json

from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.core.files.storage import default_storage
from dehaze import Dehaze
from urllib.parse import urlencode
from django.urls import reverse

# Create your views here.
def index(request):
    if request.method == "POST":
        video_file = request.FILES['video_file']
        if video_file:
            input_file = default_storage.save(video_file.name, video_file)
            output_file = f"dehaze_{input_file}"

            print(settings.MEDIA_URL)
            print(settings.MEDIA_ROOT)
            print(input_file)
            print(output_file)
            input_file_path = os.path.join(settings.MEDIA_URL, input_file)
            output_file_path = os.path.join(settings.MEDIA_URL, output_file)
            input_file = os.path.join(settings.MEDIA_ROOT, input_file)
            output_file = os.path.join(settings.MEDIA_ROOT, output_file)

            print(input_file_path)
            print(output_file_path)

            dehazer = Dehaze()
            dehazer.process_video(input_file, output_file)

            file_paths = {'input_file_path': input_file_path, 'output_file_path': output_file_path}
            print(file_paths)
            # return redirect('/results', file_paths=file_paths)
            file_paths_query_param = urlencode({'file_paths': json.dumps(file_paths)})
            url = reverse('results') + '?' + file_paths_query_param
            return redirect(url)

    return render(request, 'index.html')

def results(request):
    if request.method == "GET":
        # file_paths = request.GET.get('file_paths', None)
        # print(file_paths)

        file_paths_param = request.GET.get('file_paths', None)

        if file_paths_param is not None:
            # Deserialize the JSON data from the query parameter into a dictionary
            file_paths = json.loads(file_paths_param)
        # if file_paths is not None:
            input_file_path = file_paths.get('input_file_path', '')
            output_file_path = file_paths.get('output_file_path', '')
            return render(request, 'results.html', {'input_file_path': input_file_path, 'output_file_path': output_file_path})
        else:
            # Handle the case where file_paths is None
            return HttpResponse("File paths not found or invalid.")  
        
def contact(request):
    return render(request, 'contact.html')

def about(request):
    return render(request, 'about.html')
