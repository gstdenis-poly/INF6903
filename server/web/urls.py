from django.conf import settings
from django.conf.urls.static import static
from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('log_in/', views.log_in, name='log_in'),
    path('log_out/', views.log_out, name='log_out'),
    path('register/', views.register, name='register'),
    path('view_account/<str:account_id>/', views.view_account, name='view_account'),
    path('edit_account/<str:account_id>/', views.edit_account, name='edit_account'),
    path('download_client/', views.download_client, name='download_client'),
    path('upload_recordings/', views.upload_recordings, name='upload_recordings'),
    path('view_recording/<str:recording_id>/', views.view_recording, name='view_recording'),
    path('edit_recording/<str:recording_id>/', views.edit_recording, name='edit_recording'),
    path('view_request/<int:request_id>/', views.view_request, name='view_request'),
    path('create_request/', views.create_request, name='create_request'),
    path('delete_request/<int:request_id>/', views.delete_request, name='delete_request'),
    path('add_recording_favorite/<str:recording_id>/', views.add_recording_favorite, name='add_recording_favorite'),
    path('add_request_favorite/<int:request_id>/', views.add_request_favorite, name='add_request_favorite'),
    path('remove_recording_favorite/<str:recording_id>/', views.remove_recording_favorite, name='remove_recording_favorite'),
    path('remove_request_favorite/<int:request_id>/', views.remove_request_favorite, name='remove_request_favorite'),
] + static(settings.STATIC_URL, document_root = settings.STATIC_ROOT)