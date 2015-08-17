from django.contrib import admin
from models import Video
# Register your models here.

class VideoAdmin(admin.ModelAdmin):
    class Meta:
        model = Video

admin.site.register(Video, VideoAdmin)