import json

import requests
from django.http import HttpResponse
from django.shortcuts import render, redirect
from requests.auth import HTTPBasicAuth

from credentials import MpesaAccessToken, LipanaMpesaPpassword
from hospitalapp.forms import ImageUploadForm
from hospitalapp.models import Member, Appointment, Users, Products, ImageModel


# Create your views here.
def index(request):
    if request.method == 'POST':
        appoint = Appointment(name=request.POST['name'],
                              email=request.POST['email'],
                              phone=request.POST['phone'],
                              date=request.POST['date'],
                              department=request.POST['department'],
                              doctor=request.POST['doctor'],
                              message=request.POST['message'])
        appoint.save()
        return redirect('/')
    else:
        return render(request, 'index.html')


def inner(request):
    return render(request, 'inner-page.html')


def register(request):
    if request.method == 'POST':
        member = Member(username= request.POST['username'], email= request.POST['email'], password= request.POST['password'])
        member.save()
        return redirect('/login')
    else:
        return render(request, 'register.html')


def login(request):
    return render(request, 'login.html')



def appointmentdetails(request):
    myappoint = Appointment.objects.all()
    return render(request, 'appointmentdetails.html',{'myappoint':myappoint})

def users(request):
    myusers = Users.objects.all()
    return render(request, 'users.html', {'myusers':myusers})

def details(request):
    myproducts = Products.objects.all()
    return render(request, 'details.html', {'myproducts':myproducts})

def adminhome(request):
    if request.method == 'POST':
        if Member.objects.filter(username=request.POST['username'],
                                       password=request.POST['password']).exists():
               member = Member.objects.get(username=request.POST['username'],
                                    password=request.POST['password'])
               return render(request, 'adminhome.html', {'member':member})
        else:
             return render(request, 'login.html')

    else:
        return render(request, 'login.html')


def upload_image(request):
        if request.method == 'POST':
            form = ImageUploadForm(request.POST, request.FILES)
            if form.is_valid():
                form.save()
                return redirect('/showimages')
        else:
            form = ImageUploadForm()
            return render(request, 'upload.html', {'form': form})

def show_image(request):
        images = ImageModel.objects.all()
        return render(request, 'showimages.html', {'images': images})

def imagedelete(request, id):
        image = ImageModel.objects.get(id=id)
        image.delete()
        return redirect('/showimages')


def token(request):
    consumer_key = '1sz8KbsMbYMf3hONEn7bEz3Le1BrY7LduuayLG13AgIvswlg'
    consumer_secret = 'emjkKEBNgo8A6oRboLDunDpJzmWAZh7U9vB2lJ57BCQqWLq3evUT8juM7keZAXwX'
    api_URL = 'https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials'

    r = requests.get(api_URL, auth=HTTPBasicAuth(
        consumer_key, consumer_secret))
    mpesa_access_token = json.loads(r.text)
    validated_mpesa_access_token = mpesa_access_token["access_token"]

    return render(request, 'token.html', {"token":validated_mpesa_access_token})

def pay(request):
   return render(request, 'pay.html')



def stk(request):
    if request.method =="POST":
        phone = request.POST['phone']
        amount = request.POST['amount']
        access_token = MpesaAccessToken.validated_mpesa_access_token
        api_url = "https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest"
        headers = {"Authorization": "Bearer %s" % access_token}
        request = {
            "BusinessShortCode": LipanaMpesaPpassword.Business_short_code,
            "Password": LipanaMpesaPpassword.decode_password,
            "Timestamp": LipanaMpesaPpassword.lipa_time,
            "TransactionType": "CustomerPayBillOnline",
            "Amount": amount,
            "PartyA": phone,
            "PartyB": LipanaMpesaPpassword.Business_short_code,
            "PhoneNumber": phone,
            "CallBackURL": "https://sandbox.safaricom.co.ke/mpesa/",
            "AccountReference": "Apen Softwares",
            "TransactionDesc": "Web Development Charges"
        }
        response = requests.post(api_url, json=request, headers=headers)
        return HttpResponse(response)