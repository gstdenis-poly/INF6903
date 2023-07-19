from web.models import Account, Recording, Request
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.hashers import make_password
from django.shortcuts import redirect, render
import os
import shutil
from workers.configurator import logos_folder, uploads_folder, val_clusters_folder

# Create your views here.
def index(request):
    if request.user.is_authenticated:
        account = Account.objects.get(username = request.user.username)
        return render(request, 'logged_in/index.html', {
            'recordings': account.recordings.all()
            })
    else:
        return render(request, 'logged_out/index.html')

def log_in(request):
    if not request.POST:
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
    if not request.POST:
        return render(request, 'logged_out/register.html')
    else:
        account = Account(username = request.POST['username'],
                          email = request.POST['email'],
                          password = make_password(request.POST['password2']),
                          type = request.POST['type'],
                          company = request.POST['company'],
                          summary = request.POST['summary'])
        if 'logo' in request.FILES:
            logo_img = request.FILES['logo']
            logo_img_ext = os.path.splitext(request.FILES['logo'].name)[-1]
            db_logo_img_name = account.username + logo_img_ext
            db_logo_img_path = logos_folder + db_logo_img_name
            with open(db_logo_img_path, 'wb+') as db_logo_img:
                for c in logo_img.chunks():
                    db_logo_img.write(c)
            account.logo = db_logo_img_name
        account.save()

        return render(request, 'logged_out/register.html')

def unregister(request):
    if request.user.is_authenticated:
        account = Account.objects.get(username = request.user.username)
        account.delete()

    return render(request, 'logged_out/log_in.html')

def view_account(request, account_id):
    if request.user.is_authenticated:
        account = Account.objects.get(username = account_id)
        return render(request, 'logged_in/view_account.html', {'account' : account})
    else:
        return redirect('index')

def edit_account(request, account_id):
    if request.user.is_authenticated:
        if account_id == request.user.username:
            account = Account.objects.get(username = account_id)
            if not request.POST:
                return render(request, 'logged_in/edit_account.html', {'account' : account}) 
            else:
                account.email = request.POST['email']
                if request.POST['password2'] != '':
                    account.password = make_password(request.POST['password2'])
                account.company = request.POST['company']
                account.summary = request.POST['summary']
                if 'logo' in request.FILES:
                    logo_img = request.FILES['logo']
                    logo_img_ext = os.path.splitext(logo_img.name)[-1]
                    db_logo_img_name = account.username + logo_img_ext
                    db_logo_img_path = logos_folder + db_logo_img_name
                    if os.path.isfile(db_logo_img_path):
                        os.remove(db_logo_img_path)
                    with open(db_logo_img_path, 'wb+') as db_logo_img:
                        for c in logo_img.chunks():
                            db_logo_img.write(c)
                    account.logo = db_logo_img_name
                account.save()
                
                return redirect('/view_account/' + account_id + '/')
        else:
            return redirect('/view_account/' + account_id + '/')
    else:
        return redirect('index')

"""def download_client(request):
    if request.user.is_authenticated:
        # TODO
    else:
        # TODO

    return HttpResponse('Download client')"""

def upload_recording(request):
    if request.user.is_authenticated:
        if not request.FILES:
            return render(request, 'logged_in/upload_recording.html')
        else:
            for file in request.FILES.values():
                upload_file_path = uploads_folder + request.user.username + '-' + file.name
                with open(upload_file_path, 'wb+') as upload_file:
                    for c in file.chunks():
                        upload_file.write(c)
            
                upload_folder_path = os.path.splitext(upload_file_path)[0]
                shutil.unpack_archive(upload_file_path, upload_folder_path, 'zip')
                os.remove(upload_file_path) # Remove .zip file after uncompressing it
                open(upload_folder_path + '.final', 'w').close() # .final file for worker notif

            return render(request, 'logged_in/upload_recording.html')
    else:
        return redirect('index')

def view_recording(request, recording_id):
    if request.user.is_authenticated:
        recording = Recording.objects.get(id = recording_id)
        results_file_path = val_clusters_folder + recording_id + '.txt'

        solutions = []
        if os.path.isfile(results_file_path):
            results_file = open(results_file_path, 'r')
            results_file_lines = results_file.read().splitlines()
            results_file.close()

            for line in results_file_lines:
                print(line)
                solutions += [Recording.objects.get(id = line.split('|')[0])]

        return render(request, 'logged_in/view_recording.html', {
            'recording': recording, 'solutions': solutions,
            })
    else:
        return redirect('index')
    
def edit_recording(request, recording_id):
    if request.user.is_authenticated:
        recording = Recording.objects.get(id = recording_id)
        if request.user.username != recording.account.username:
            return redirect('/view_recording/' + recording_id + '/')
        elif not request.POST:
            return render(request, 'logged_in/edit_recording.html', {'recording': recording})
        else:
            recording.title = request.POST['title']
            recording.save()

            return redirect('/view_recording/' + recording_id + '/')
    else:
        return redirect('index')

def create_request(request):
    if request.user.is_authenticated:
        account = Account.objects.get(username = request.user.username)
        if account.type == 'provider':
            return redirect('index')
        elif not request.POST:
            return render(request, 'logged_in/create_request.html', {
                'recordings': account.recordings.all()
                })
        else:
            req = Request(account = account)
            req.save()
            for key in request.POST:
                if 'video' in key:
                    req.recordings.add(Recording.objects.get(id = request.POST[key]))
            req.save()    
            
            return redirect('index')
    else:
        return redirect('index')
    
def view_request(request, request_id):
    if request.user.is_authenticated:
        req = Request.objects.get(id = request_id)
        return render(request, 'logged_in/view_request.html', {
            'req': req,
            'recordings': req.recordings.all()
            })
    else:
        return redirect('index')

def edit_request(request, request_id):
    if request.user.is_authenticated:
        req = Request.objects.get(id = request_id)
        if request.user.username != req.account.username:
            return redirect('/view_request/' + str(request_id) + '/')
        elif not request.POST:
            return render(request, 'logged_in/edit_request.html', {
                'req': req,
                'req_recordings': req.recordings.all(),
                'acc_recordings': req.account.recordings.all()
                })
        else:
            req.recordings.clear()
            for key in request.POST:
                if 'video' in key:
                    req.recordings.add(Recording.objects.get(id = request.POST[key]))
            req.save() 

            return redirect('/view_request/' + str(request_id) + '/')
    else:
        return redirect('index')

def delete_request(request, request_id):
    if request.user.is_authenticated:
        req = Request.objects.get(id = request_id)
        req.delete()
    
    return redirect('index')

"""def view_solution(request, solution_id):
    if request.user.is_authenticated:
        # TODO
    else:
        # TODO

    return HttpResponse('Solution %s.' % solution_id)"""