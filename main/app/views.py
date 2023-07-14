from app.models import Account
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.hashers import make_password
from django.http import HttpResponse
from django.shortcuts import redirect, render

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
                          summary = request.POST['summary'],
                          logo = request.POST['logo'])
        account.save()

        return render(request, 'logged_out/register.html')

"""def unregister(request, user_id):
    if request.user.is_authenticated:
        # TODO
    else:
        # TODO

    return HttpResponse('Unregister %s.' % user_id)

def view_account(request, user_id):
    if request.user.is_authenticated:
        # TODO
    else:
        # TODO

    return HttpResponse('View account %s.' % user_id)

def edit_account(request, user_id):
    if request.user.is_authenticated:
        # TODO
    else:
        # TODO

    return HttpResponse('Edit account %s.' % user_id)

def download_client(request):
    if request.user.is_authenticated:
        # TODO
    else:
        # TODO

    return HttpResponse('Download client')

def upload_recording(request):
    if request.user.is_authenticated:
        # TODO
    else:
        # TODO

    return HttpResponse('Upload recording')

def view_request(request, request_id):
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