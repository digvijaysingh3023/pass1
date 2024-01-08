from django.shortcuts import render,redirect
from django.http import JsonResponse
from . models import Pass
from django.core.mail import EmailMessage
from django.core.mail import send_mail
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.utils import timezone
import random
import string
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
    transactions_ref = database.collection('transactions').stream()

    transactions = []
    for transaction in transactions_ref:
        transaction_dict = transaction.to_dict()
        transaction_dict['id'] = transaction.id

        # Fetch user data from 'verified_users' collection
        user_ref = database.collection('verified_users').document(transaction_dict['user']).get()
        user_dict = user_ref.to_dict()
        transaction_dict['user'] = user_dict

        transactions.append(transaction_dict)

    return render(request, 'main/order_summary.html', {'transactions': transactions})
def unique_id(length):
    while True:
        random_string = ''.join(random.choices(string.ascii_letters + string.digits, k=length))
        if random_string not in used_strings:
            used_strings.add(random_string)
            return random_string
used_strings = set()
def savedata(request):
    if request.method == 'POST':
        id = unique_id(5)
        amount = 750
        status="Pending"
        err_des={
            'error':0,
            'pass':1,
        }
        # fee_id = "M1006"
        # paases_type = {
        #     'general': 0,
        #     'premium': 0,
        #     'exclusive': 0,
        #     'id': id,
        #     'amount': 0,
        # }
        time=timezone.now()
        LeaderName = request.POST.get('LeaderName')
        Lpasstype = request.POST.get('Lpasstype')
        LeaderContact_no = request.POST.get('LeaderContact_no')
        LeaderEmail = request.POST.get('LeaderEmail')
        LeaderIDType = request.POST.get('LeaderIDtype')
        LeaderIDNumber = request.POST.get('LeaderIDnumber')
        LeaderAge = request.POST.get('LeaderAge')
        LeaderGender = request.POST.get('LeaderGender')
        membernames = request.POST.getlist('name')
        member_contacts = request.POST.getlist('contact_no')
        member_passtype = request.POST.getlist('pass_type')
        member_idtype = request.POST.getlist('IDtype')
        member_idnumber = request.POST.getlist('IDnumber')
        member_age = request.POST.getlist('age')
        member_gender = request.POST.getlist('gender')
        member_email = request.POST.getlist('email')
        Tdata = {
            "Email": LeaderEmail,
            "time":time,
            "amount":amount,
            "err_des":err_des,
            "status":status,
            
        }
        Ldata={
            "Email": LeaderEmail,
            "LName": LeaderName,
            "LContact": LeaderContact_no,
            "LIDType": LeaderIDType,
            "LIDNumber": LeaderIDNumber,
            'Lpasstype':Lpasstype,
            "LAge": LeaderAge,
            "LGender": LeaderGender,
        }
        doc_ref = database.collection('transaction').document(id)
        doc_ref.set(Tdata)
        doc_ref.collection('users').document().set(Ldata)
        members = []
        for fname,contact, pass_type, idtype, idnumber, gender, age, email, in zip(membernames, member_contacts, member_passtype, member_idtype, member_idnumber, member_gender, member_age, member_email):
            member = {
                "name": fname,
                "contact": contact,
                "pass_type": pass_type,
                "id_type": idtype,
                "id_number": idnumber,
                "age": age,
                "gender": gender,
                'email': email,
            }
            doc_ref.collection('users').document().set(member)
            members.append(member)
    return render(request, 'main/confirm_payment.html',{'leader':Ldata,'Member':members})