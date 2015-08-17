from django.conf.urls import patterns, include, url

urlpatterns = patterns('',
    url(r'^$', 'vids.views.home', name='home'),
    url(r'^upload_video/$', 'vids.views.upload_video', name='upload_video'),
    url(r'^video/(?P<video_pk>\d+)/$', 'vids.views.video_detail', name='video_detail'),
)