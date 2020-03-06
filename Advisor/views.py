from django.shortcuts import render, redirect
from django.contrib.auth import authenticate
from Advisor.models import Users
from Advisor.controllers import indexController, superuserController
from django.http import JsonResponse

# Create your views here.

def updatedeps(request):
    return superuserController.updateDeps(request)

def updatehod(request):
    return superuserController.updateHod(request)


def getHods(request):
    return superuserController.hods(request)


def index(request):
    return indexController.index(request)


def dashboard(request):
    return indexController.dashboard(request)


def settings(request):
    if 'user' in request.session:
        context = {'user': Users.objects.get(id=request.session['user'])}
        return render(request, 'Master\settings.html', context)
    else:
        return redirect(index)


def editAdmins(request):
    return superuserController.editAdmins(request)


def logout(request):
    return indexController.log(request)


def changePass(request):
    if request.method == 'POST':
        use = Users.objects.get(id=request.session['user'])
        use.set_password(request.POST['password'])
        use.save()
        data = {
            'Changed': True
        }
        return JsonResponse(data)
    else:
        return render(settings)
