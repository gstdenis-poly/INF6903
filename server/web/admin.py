from django.contrib import admin
from .models import *

# Register your models here.
admin.site.register(Account)
admin.site.register(Recording)
admin.site.register(Request)
admin.site.register(Monitor)
admin.site.register(KeyboardEvent)
admin.site.register(MouseEvent)
admin.site.register(Favorite)
admin.site.register(RecordingFavorite)
admin.site.register(RequestFavorite)