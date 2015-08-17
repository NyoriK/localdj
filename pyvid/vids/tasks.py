import logging
logger = logging.getLogger(__name__)

from pyvid.celery import app

from time import time

from models import Video

import re

def get_upload_file_name(video):
    original_name = video.title
    return "%s_%s" % (str(time()).replace('.', '_'), re.sub(r'[^a-zA-Z0-9_-]', '',original_name))

def timer(start_time,end_time):
    hours, rem = divmod(end_time-start_time, 3600)
    minutes, seconds = divmod(rem, 60)
    return ("{:0>2}:{:0>2}:{:05.2f}".format(int(hours),int(minutes),seconds))


from pyvid.settings import MEDIA_ROOT

from django.core.files import File

import os

from subprocess import Popen


# Single pass Multiple encdoing

@app.task
def convert_video(video_id):
    video = Video.objects.get(id=video_id)

    # If on same machine
    video_path = str(MEDIA_ROOT)+'/'+str(video.original_video)

    name = str(get_upload_file_name(video))
    convert_video_name_720 = '720-'+ name +'.mp4'
    convert_video_name_480 = '480-'+ name +'.mp4'
    poster_name = name+'.jpg'

    cmd = """
        ffmpeg -i %s \
            -codec:v libx264 -tune zerolatency -profile:v high -preset faster -crf 23 -maxrate 1200k -bufsize 12000k -vf scale="trunc(oh*a/2)*2:720" -codec:a libfdk_aac -pix_fmt yuv420p -movflags +faststart -threads 0 %s \
            -codec:v libx264 -tune zerolatency -profile:v main -preset faster -crf 23 -maxrate 500k -bufsize 5000k -vf scale="trunc(oh*a/2)*2:480" -codec:a libfdk_aac -pix_fmt yuv420p -movflags +faststart -threads 0 %s && \
        ffmpeg -i %s -ss 00:00:01.000 -vframes 1 %s
        """ % (video_path, convert_video_name_720, convert_video_name_480, video_path, poster_name)
    start_time = time()
    proc = Popen(
        cmd,
        shell=True
    )
    proc.wait()

    if proc.returncode == 0:
        end_time = time()
        time_taken = timer(start_time, end_time)
        fp_720 = open(convert_video_name_720)
        fp_480 = open(convert_video_name_480)
        fp_poster = open(poster_name)
        myfile_720 = File(fp_720)
        myfile_480 = File(fp_480)
        myfile_poster = File(fp_poster)
        video.mp4_720.save(name=convert_video_name_720, content=myfile_720)
        video.mp4_480.save(name=convert_video_name_480, content=myfile_480)
        video.poster.save(name=poster_name, content=myfile_poster)
        video.time_taken = time_taken
        video.converted = True
        video.save()
        os.remove(convert_video_name_720)
        os.remove(convert_video_name_480)
        os.remove(poster_name)
    else:
        # Do something / Inform user in notification
        pass




# Two pass Multiple encoding


# @app.task
# def convert_video(video_id):
#     video = Video.objects.get(id=video_id)

#     # If on same machine
#     video_path = str(MEDIA_ROOT)+'/'+str(video.original_video)

#     # # For s3
#     # # video_path = video.original_video.url
#     # # or
#     # video_path = str(MEDIA_URL) + str (video.original_video)
#     unique_pass_id_720 = str(get_upload_file_name(video))+'720'
#     unique_pass_id_480 = str(get_upload_file_name(video))+'480'
#     convert_video_name_720 = '720-'+str(get_upload_file_name(video))+'.mp4'
#     convert_video_name_480 = '480-'+str(get_upload_file_name(video))+'.mp4'

#     cmd = """
#             ffmpeg -i %s \
#                 -codec:v libx264 -tune zerolatency -profile:v main -preset superfast -b:v 1000k -maxrate 1000k -bufsize 10000k -vf scale="trunc(oh*a/2)*2:720" -threads 0 -pix_fmt yuv420p  -movflags +faststart -pass 1 -passlogfile %s -an -f mp4 -y /dev/null \
#                 -codec:v libx264 -tune zerolatency -profile:v baseline -level 3.0 -preset superfast -b:v 500k -maxrate 500k -bufsize 5000k -vf scale="trunc(oh*a/2)*2:480" -threads 0 -pix_fmt yuv420p  -movflags +faststart -pass 1 -passlogfile %s -an -f mp4 -y /dev/null && \
#             ffmpeg -i %s \
#                 -codec:v libx264 -tune zerolatency -profile:v main -preset superfast -b:v 1000k -maxrate 1000k -bufsize 10000k -vf scale="trunc(oh*a/2)*2:720" -threads 0 -pix_fmt yuv420p -pass 2 -passlogfile %s -codec:a libfdk_aac -movflags +faststart %s \
#                 -codec:v libx264 -tune zerolatency -profile:v baseline -level 3.0 -preset superfast -b:v 500k -maxrate 500k -bufsize 5000k -vf scale="trunc(oh*a/2)*2:480" -threads 0 -pass 2 -passlogfile %s -codec:a libfdk_aac -pix_fmt yuv420p -movflags +faststart %s
#         """ % (video_path, unique_pass_id_720, unique_pass_id_480, video_path, unique_pass_id_720, convert_video_name_720, unique_pass_id_480, convert_video_name_480)
#     start_time = time()
#     proc = Popen(
#         cmd,
#         shell=True
#     )
#     proc.wait()

#     if proc.returncode == 0:
#         end_time = time()
#         time_taken = timer(start_time, end_time)
#         fp_720 = open(convert_video_name_720)
#         fp_480 = open(convert_video_name_480)
#         myfile_720 = File(fp_720)
#         myfile_480 = File(fp_480)
#         video.mp4_720.save(name=convert_video_name_720, content=myfile_720)
#         video.mp4_480.save(name=convert_video_name_480, content=myfile_480)
#         video.time_taken = time_taken
#         video.converted = True
#         video.save()
#         os.remove(convert_video_name_720)
#         os.remove(convert_video_name_480)
#         os.remove(unique_pass_id_720+'-0.log')
#         os.remove(unique_pass_id_480+'-0.log')
#     else:
#         # Do something / Inform user in notification
#         pass
