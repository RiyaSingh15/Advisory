from django.core import mail
from django.utils.html import strip_tags
from django.template.loader import render_to_string
from django.shortcuts import render, redirect
from Advisor.models import students, Class, department, detailed_Marks, Subjects, Pincodes
from django.http import JsonResponse
from django.core import serializers
from django.db.models import Q
import os
from PIL import Image
import json


# Create your views here.

def imageStu(request):
    return render(request, 'Mentors/uploadImage.html')


def getPin(request):
    if 'user' in request.session:
        pins = Pincodes.objects.filter(Pincode=request.POST['id'])
        if len(pins) == 1:
            data = {
                'success': True,
                'City': pins[0].District.title(),
                'District': pins[0].District.title(),
                'State': pins[0].State.title(),
            }
        else:
            data = {
                'success': False
            }
        return JsonResponse(data)


def index(request):
    if 'user' in request.session:
        if request.user.admin:
            Classes = Class.objects.filter(
                department=request.user.teacher.department).values('id', 'section', 'batch').order_by('-batch')
            context = {
                'Class': Classes,
            }
            return render(request, 'Mentors/Students.html', context)
        elif request.user.is_superuser:
            return redirect('Advisor:dashboard')
        else:
            return render(request, 'Mentors/Students.html')
    else:
        return redirect('Advisor:index')


def createStudent(request):
    if 'user' in request.session:
        dat = json.loads(request.POST['student'])
        clas = Class.objects.get(Mentor=request.user.teacher)
        s = students(Class=clas, **dat)
        s.save()
        data = {
            'success': True,
        }
        return JsonResponse(data)


def updatedStu(request):
    if 'user' in request.session:
        if request.method == 'POST':
            values = {k: v for k, v in request.POST.items()}
            values.pop('csrfmiddlewaretoken')
            student = students.objects.filter(
                urn=values.pop('urn')).update(**values)
            return redirect('Mentor:students')


def deleteStudent(request):
    if 'user' in request.session:
        student = students.objects.get(id=request.POST['student'])
        student.delete()
        data = {
            'success': True,
            'student': student,
        }
        return JsonResponse(data)


def getStudent(request):
    try:
        student = students.objects.get(urn=request.POST['student'])
    except students.DoesNotExist:
        data = {
            'success': False,
            'message': 'No such User',
        }
        return JsonResponse(data)
    dm = detailed_Marks.objects.filter(student=student).values(
        'exam_date', 'semester', 'Sgpa', 'subject__Name', 'subject__credits', 'subject', 'passive_back')
    for d in dm:
        d['exam_date'] = str(d['exam_date'])
    data = {
        'success': True,
        'marks': list(dm),
        'student': serializers.serialize(
            'json', [student, student.Class, student.Class.department], indent=2, use_natural_foreign_keys=True),
    }
    return JsonResponse(data)


def getStudents(request):
    if 'user' in request.session:
        if request.user.is_superuser:
            return redirect(request, 'Advisor:dashboard')
        elif request.user.admin:
            if request.POST['class'] == 'ALL':
                Classes = Class.objects.filter(
                    department=request.user.teacher.department)
            else:
                Classes = [Class.objects.get(id=request.POST['class'])]
            student = students.objects.filter(Q(full_name__contains=request.POST['term']) | Q(
                crn__contains=request.POST['term']) | Q(urn__contains=request.POST['term']), Class__in=Classes)
        else:
            Clas = Class.objects.get(Mentor=request.user.teacher)
            student = students.objects.filter(Q(full_name__contains=request.POST['term']) | Q(
                crn__contains=request.POST['term']) | Q(urn__contains=request.POST['term']), Class=Clas)
        rec = serializers.serialize(
            'json', student, indent=2, use_natural_foreign_keys=True)
        data = {
            'success': True,
            'student': rec,
        }
        return JsonResponse(data)


def updateSProf(request):
    if 'user' in request.session:
        if request.method == 'POST':
            return render(request, 'Mentors/updateStu.html', {'student': students.objects.get(urn=request.POST['student'])})


def updateStudent(request):
    student = students.objects.get(urn=request.POST['urn'])
    if student.Father_pic:
        os.remove('Media/'+student.Father_pic.name)
    if student.Mother_pic:
        os.remove('Media/'+student.Mother_pic.name)
    if student.photo:
        os.remove('Media/'+student.photo.name)
    student.Father_pic = request.FILES['Father_pic']
    student.Mother_pic = request.FILES['Mother_pic']
    student.photo = request.FILES['photo']
    student.Father_pic.name = str(student.urn)+'.jpg'
    student.Mother_pic.name = str(student.urn)+'.jpg'
    student.photo.name = str(student.urn)+'.jpg'
    student.save()

    rec = serializers.serialize(
        'json', [student], indent=2, use_natural_foreign_keys=True)
    data = {
        'success': True,
        'student': rec,
    }
    return JsonResponse(data)


def notification(request):
    if 'user' in request.session:
        if request.method == 'POST':
            subject = 'Upload your pics'
            conx = {'host': request.get_host()+'/picture-upload'}
            html_message = render_to_string(
                'Mails/uploadpic.html', conx)
            plain_message = strip_tags(html_message)
            from_email = request.user.teacher.full_name
            mail.send_mail(subject, plain_message, from_email, [key['email'] for key in students.objects.filter(
                urn__in=request.POST.getlist('receiver[]')).values('email')], html_message=html_message)
            data = {
                'success': True
            }
            return JsonResponse(data)
        else:
            context = {
                'students': students.objects.filter(Class__Mentor=request.user.teacher).values('urn', 'full_name')
            }
            return render(request, 'Mentors/notification.html', context)
    else:
        return redirect(request, 'Advisor:index')
