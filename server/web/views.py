from web.models import Account
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.hashers import make_password
from django.http import HttpResponse
from django.shortcuts import redirect, render
import os
import shutil
from workers.configurator import logos_folder, uploads_folder

# Create your views here.
def index(request):
    if request.user.is_authenticated:
        return render(request, 'logged_in/index.html')
    else:
        return render(request, 'logged_out/index.html')

def log_in(request):
    if 'username' not in request.POST:
        return render(request, 'logged_out/log_in.html')
    else:
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username = username, password = password)
        if user is not None:
            login(request, user)
            return redirect('index')
        else:
            return render(request, 'logged_out/log_in.html')
    
def log_out(request):
    logout(request)
    return redirect('index')

def register(request):
    if 'username' not in request.POST:
        return render(request, 'logged_out/register.html')
    else:
        account = Account(username = request.POST['username'],
                          email = request.POST['email'],
                          password = make_password(request.POST['password1']),
                          type = request.POST['type'],
                          company = request.POST['company'],
                          summary = request.POST['summary'])
        if 'logo' in request.FILES:
            logo_img = request.FILES['logo']
            logo_img_ext = os.path.splitext(request.FILES['logo'].name)[-1]
            db_logo_img_path = logos_folder + account.username + logo_img_ext
            with open(db_logo_img_path, 'wb+') as db_logo_img:
                for c in logo_img.chunk():
                    db_logo_img.write(c)
            account.logo = db_logo_img_path
        account.save()

        return render(request, 'logged_out/register.html')

def unregister(request):
    if request.user.is_authenticated:
        account = Account.objects.get(username = request.user.username)
        account.delete()

    return render(request, 'logged_out/log_in.html')

def view_account(request, user_id):
    if request.user.is_authenticated:
        account = Account.objects.get(username = request.user.username)
        return render(request, 'logged_in/view_account.html', {'account' : account})
    else:
        return render(request, 'logged_out/index.html')

def edit_account(request, user_id):
    account = Account.objects.get(username = request.user.username)
    if request.user.is_authenticated:
        if user_id == account.username:
            if 'username' in request.POST:
                account.email = request.POST['email']
                account.password = make_password(request.POST['password1'])
                account.company = request.POST['company']
                account.summary = request.POST['summary']
                if 'logo' in request.FILES:
                    logo_img = request.FILES['logo']
                    logo_img_ext = os.path.splitext(logo_img.name)[-1]
                    db_logo_img_path = logos_folder + account.username + logo_img_ext
                    with open(db_logo_img_path, 'wb+') as db_logo_img:
                        for c in logo_img.chunk():
                            db_logo_img.write(c)
                    account.logo = db_logo_img_path
                account.save()
                
                return render(request, 'logged_in/edit_account.html', {'account' : account})
            else:
                return render(request, 'logged_in/edit_account.html', {'account' : account}) 
        else:
            return render(request, 'logged_in/view_account.html', {'account' : account})
    else:
        return render(request, 'logged_out/index.html')

"""def download_client(request):
    if request.user.is_authenticated:
        # TODO
    else:
        # TODO

    return HttpResponse('Download client')"""

def upload_recording(request):
    if request.user.is_authenticated:
        if request.FILES:
            for file in request.FILES:
                upload_file_path = uploads_folder + file.name
                with open(upload_file_path, 'wb+') as upload_file:
                    for c in file.chunk():
                        upload_file.write(c)
            
                upload_folder_name = uploads_folder + os.path.splitext(file.name)[0]
                shutil.unpack_archive(upload_file_path, upload_folder_name, 'zip')
                os.remove(upload_file_path) # Remove .zip file after uncompressing it
                open(upload_folder_name + '.final', 'w').close() # .final file for worker notif

            return render(request, 'logged_in/upload_recording.html')
        else:
            return render(request, 'logged_in/upload_recording.html')
    else:
        return render(request, 'logged_out/index.html')

"""def view_request(request, request_id):
    if request.user.is_authenticated:
        # TODO
    else:
        # TODO

    return HttpResponse('View request %s.' % request_id)

def edit_request(request, request_id):
    if request.user.is_authenticated:
        # TODO
    else:
        # TODO

    return HttpResponse('Edit request %s.' % request_id)

def create_request(request):
    if request.user.is_authenticated:
        # TODO
    else:
        # TODO

    return HttpResponse('Create request.')

def delete_request(request, request_id):
    if request.user.is_authenticated:
        # TODO
    else:
        # TODO

    return HttpResponse('Delete request %s.' % request_id)

def view_solution(request, solution_id):
    if request.user.is_authenticated:
        # TODO
    else:
        # TODO

    return HttpResponse('Solution %s.' % solution_id)"""