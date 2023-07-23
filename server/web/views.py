from web.models import Account, Recording, Request
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.shortcuts import redirect, render
import functools
import os
import shutil
from server.settings import CLIENT_DIR, LOGOS_DIR, UPLOADS_DIR

# Create your views here.
def index(request):
    if request.user.is_authenticated:
        account = Account.objects.get(username = request.user.username)
        return render(request, 'logged_in/index.html', {
            'account': account,
            'recordings': account.recordings.all(),
            'requests': account.requests.all()
            })
    else:
        return render(request, 'logged_out/index.html')

def log_in(request):
    if not request.POST:
        return redirect('index')
    else:
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username = username, password = password)
        if user is not None:
            login(request, user)
            return HttpResponse('OK')
        else:
            return HttpResponse('Wrong credentials', status = 401)
    
def log_out(request):
    if request.user.is_authenticated:
        logout(request)

    return redirect('index')

def register(request):
    if not request.POST:
        return redirect('index')
    else:
        username = request.POST['username']
        password = request.POST['password2']
        email = request.POST['email']
        try:
            user = User.objects.get(username = username)
            return HttpResponse('Username already used', status = 400)
        except User.DoesNotExist:
            try:
                user = User.objects.get(email = email)
                return HttpResponse('Email already used', status = 400)
            except User.DoesNotExist:
                pwd1, pwd2 = request.POST['password1'], request.POST['password2']
                if pwd1 != pwd2:
                    return HttpResponse('Passwords must be identical', status = 400)

                account = Account(username = username, email = email,
                                  password = make_password(pwd2),
                                  type = request.POST['type'],
                                  company = request.POST['company'],
                                  summary = request.POST['summary'])
                if 'logo' in request.FILES:
                    logo_img = request.FILES['logo']
                    logo_img_ext = os.path.splitext(request.FILES['logo'].name)[-1]
                    db_logo_img_name = account.username + logo_img_ext
                    db_logo_img_path = LOGOS_DIR + db_logo_img_name
                    with open(db_logo_img_path, 'wb+') as db_logo_img:
                        for c in logo_img.chunks():
                            db_logo_img.write(c)
                    account.logo = db_logo_img_name
                account.save()
                
                user = authenticate(request, username = username, password = password)
                login(request, user)
        
        return HttpResponse('OK')

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
                return redirect('index') 
            else:
                pwd1, pwd2 = request.POST['password1'], request.POST['password2']
                password_changed = not (pwd1 == '' and pwd2 == '')
                if password_changed:
                    if pwd1 != pwd2:
                        return HttpResponse('Passwords must be identical', status = 400)
                    account.password = make_password(pwd2)

                account.email = request.POST['email']
                account.company = request.POST['company']
                account.summary = request.POST['summary']
                if 'logo' in request.FILES:
                    logo_img = request.FILES['logo']
                    logo_img_ext = os.path.splitext(logo_img.name)[-1]
                    db_logo_img_name = account.username + logo_img_ext
                    db_logo_img_path = LOGOS_DIR + db_logo_img_name
                    if os.path.isfile(db_logo_img_path):
                        os.remove(db_logo_img_path)
                    with open(db_logo_img_path, 'wb+') as db_logo_img:
                        for c in logo_img.chunks():
                            db_logo_img.write(c)
                    account.logo = db_logo_img_name
                account.save()

                if password_changed:
                    user = authenticate(request, username = account_id, password = pwd2)
                    login(request, user)
                
                return HttpResponse('OK')
        else:
            return redirect('/view_account/' + account_id + '/')
    else:
        return redirect('index')

def download_client(request):
    if request.user.is_authenticated:
        client_zip_name = 'recorder.zip'
        client_zip_path = CLIENT_DIR + client_zip_name
        response = HttpResponse(open(client_zip_path, 'rb'), content_type = 'application/zip')
        response['Content-Disposition'] = 'attachment; filename=' + client_zip_name
        return response
    else:
        return redirect('index')

def upload_recordings(request):
    if request.user.is_authenticated or not request.FILES:
        for file in request.FILES.values():
            upload_file_path = UPLOADS_DIR + request.user.username + '-' + file.name
            with open(upload_file_path, 'wb+') as upload_file:
                for c in file.chunks():
                    upload_file.write(c)
        
            upload_folder_path = os.path.splitext(upload_file_path)[0]
            shutil.unpack_archive(upload_file_path, upload_folder_path, 'zip')
            os.remove(upload_file_path) # Remove .zip file after uncompressing it
            open(upload_folder_path + '.final', 'w').close() # .final file for worker notif
        
        return HttpResponse('OK')
    else:
        return redirect('index')

def view_recording(request, recording_id):
    if request.user.is_authenticated:
        recording = Recording.objects.get(id = recording_id)

        solutions = recording.get_relevant_solutions()
        cmp_key = functools.cmp_to_key(Recording.cmp_solutions_score)
        solutions.sort(key = cmp_key) # Sort solutions by ergonomic score

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
        if account.type == 'provider' or not request.POST:
            return redirect('index')
        else:
            req = Request(account = account)
            req.save()
            for recording_id in request.POST['recordings']:
                req.recordings.add(Recording.objects.get(id = recording_id))
            req.save() 
            
            return HttpResponse('OK')
    else:
        return redirect('index')
    
def view_request(request, request_id):
    if request.user.is_authenticated:
        req = Request.objects.get(id = request_id)

        solutions = req.get_relevant_solutions()
        cmp_key = functools.cmp_to_key(Request.cmp_solutions_score)
        solutions = sorted(solutions.items(), key = cmp_key) # Sort solutions by ergonomic score

        return render(request, 'logged_in/view_request.html', {
            'req': req,
            'recordings': req.recordings.all(),
            'solutions' : solutions
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