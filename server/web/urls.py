from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('log_in/', views.log_in, name='log_in'),
    path('log_out/', views.log_out, name='log_out'),
    path('register/', views.register, name='register'),
    path('unregister', views.unregister, name='unregister'),
    path('view_account/<str:account_id>/', views.view_account, name='view_account'),
    path('edit_account/<str:account_id>/', views.edit_account, name='edit_account'),
    #path('download_client/', views.download_client, name='download_client'),
    path('upload_recording/', views.upload_recording, name='upload_recording'),
    #path('view_request/<int:request_id>/', views.view_request, name='view_request'),
    #path('edit_request/<int:request_id>/', views.edit_request, name='edit_request'),
    #path('create_request/', views.create_request, name='create_request'),
    #path('delete_request/<int:request_id>/', views.delete_request, name='delete_request'),
    #path('view_solution/<int:solution_id>/', views.view_solution, name='view_solution'),
]