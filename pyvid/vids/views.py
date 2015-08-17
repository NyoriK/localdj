from django.http import HttpResponseRedirect
from django.shortcuts import render

from models import Video
from forms import VideoForm
from tasks import convert_video

def home(request):
    videos = Video.objects.all()

    return render(request, 'home.html', {
        'videos':videos
    })

def upload_video(request):
    if request.POST:
        form = VideoForm(request.POST, request.FILES)
        if form.is_valid():
            video = form.save(commit=False)
            video.save()
            convert_video.delay(video.id)
            return HttpResponseRedirect('/')
    else:
        form = VideoForm()
    return render(request, 'upload_video.html', {
        'form':form
    })

def video_detail(request, video_pk):
    video = Video.objects.get(pk=video_pk)

    return render(request, 'video.html', {
        'video':video
    })
