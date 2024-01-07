from django.shortcuts import render,redirect
from django.http import JsonResponse
from . models import Pass
from django.core.mail import EmailMessage
from django.core.mail import send_mail
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
import random
import json
import pyrebase


config = {
   'apiKey': "AIzaSyCYBAFlRDVF_niUuOzk-dc4lo8v5XOg2cs",
  'authDomain': "passportal-68a8a.firebaseapp.com",
  'databaseURL': "https://passportal-68a8a-default-rtdb.asia-southeast1.firebasedatabase.app",
  'projectId': "passportal-68a8a",
  'storageBucket': "passportal-68a8a.appspot.com",
  'messagingSenderId': "28735319650",
  'appId': "1:28735319650:web:5e1095ba7fdb52f4182b3b",
}

firebase=pyrebase.initialize_app(config)
authe = firebase.auth()
database=firebase.database()



# Create your views here.
def home(request):
    passes=Pass.objects.all()
    name = database.child('Data').child('Name').get().val()
    return render(request, 'main/home.html',{'passes':passes, 'name': name})

def otp(request):
    context = {
        'message': "Please Enter E-mail First",
    }
    return render(request, "main/otp.html", context)

@csrf_exempt
def sendOtp(request):
    try:
        email = json.loads(request.body)['email']
        request.session['LeaderEmail'] = email
        otp = random.randint(100000, 999999)
        subject = 'Your email verification'
        message = 'Your otp for verifiction of your email is ' + str(otp)
        from_email = settings.EMAIL_HOST_USER
        send_mail(subject, message, from_email, [email])

        doc_ref = database.collection('all_otps').document()

        doc_ref.set({
            'email': email,
            'otp': otp,
        })
        
        
    except Exception as e:
        print(e)
    return JsonResponse({"otp": "otp"})


def verify_otp(request):
    otp = request.POST.get('otp')
    

def order_summary(request):
    # Fetch transaction data from Firebase
    transactions_ref = db.collection('transactions').stream()

    transactions = []
    for transaction in transactions_ref:
        transaction_dict = transaction.to_dict()
        transaction_dict['id'] = transaction.id

        # Fetch user data from 'verified_users' collection
        user_ref = db.collection('verified_users').document(transaction_dict['user']).get()
        user_dict = user_ref.to_dict()
        transaction_dict['user'] = user_dict

        transactions.append(transaction_dict)

    return render(request, 'main/order_summary.html', {'transactions': transactions})