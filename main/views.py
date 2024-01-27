from django.shortcuts import render,redirect
from django.http import JsonResponse
from .models import Pass
from django.core.mail import EmailMessage
from django.core.mail import send_mail
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.utils import timezone
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
import random
import string
import random
import json
import pyrebase 
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes

@api_view(['GET'])
def user_data(request):
    try:
        email = request.GET.get('email')
        if not email:
            return Response({'error': 'Email is required'}, status=status.HTTP_400_BAD_REQUEST)

        user_ref = db.collection('transaction').where('email', '==', email).stream()
        users = []
        for user in user_ref:
            user_dict = user_ref.to_dict()
            # user_dict['id'] = user.id
            users.append(user_dict)

        if not users:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

        user = users[0]
        has_passes = bool(user.get('passes', []))

        if has_passes:
            # Encrypt user data as needed
            encrypted_data = encrypt_user_data(user)
            return Response({'data': encrypted_data})
        else:
            return Response({'error': 'User has no passes'}, status=status.HTTP_404_NOT_FOUND)

    except Exception as e:
        print(e)
        return Response({'error': 'An error occurred'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

def encrypt_user_data(user):
    # Implement your encryption logic here
    # For example, using the PyCryptoDome library
 

    key = get_random_bytes(32)
    cipher = AES.new(key, AES.MODE_EAX)
    ciphertext, tag = cipher.encrypt_and_digest(json.dumps(user).encode())
    nonce = cipher.nonce

    # Combine nonce, tag, and ciphertext into a single string
    encrypted_data = nonce + tag + ciphertext

    return encrypted_data
config = {
   'apiKey': "AIzaSyCYBAFlRDVF_niUuOzk-dc4lo8v5XOg2cs",
  'authDomain': "passportal-68a8a.firebaseapp.com",
  'databaseURL': "https://passportal-68a8a-default-rtdb.asia-southeast1.firebasedb.app",
  'projectId': "passportal-68a8a",
  'storageBucket': "passportal-68a8a.appspot.com",
  'messagingSenderId': "28735319650",
  'appId': "1:28735319650:web:5e1095ba7fdb52f4182b3b",
}

# firebase=pyrebase.initialize_app(config)
# authe = firebase.auth()
# database=firebase.database()
cred = credentials.Certificate('main/serviceAccountCredentials.json')
firebase_admin.initialize_app(cred)
db = firestore.client()


# Create your views here.

def home(request):
    context={
        'EarlyBird':{
        'date':db.child('Data').child('Date').child('Early-Bird').get().val(),
        'price':db.child('Data').child('Price').child('Early-Bird').get().val(),
        'img':db.child('Data').child('Image').child('Early-Bird').get().val()
        },
        'Normal':{
        'date':db.child('Data').child('Date').child('Normal').get().val(),
        'price':db.child('Data').child('Price').child('Normal').get().val(),
        'img':db.child('Data').child('Image').child('Normal').get().val()
        },
        'Day1':{
        'date':db.child('Data').child('Date').child('Day 1').get().val(),
        'price':db.child('Data').child('Price').child('Day').get().val(),
        'img':db.child('Data').child('Image').child('Day 1').get().val()
        },
        'Day2':{
        'date':db.child('Data').child('Date').child('Day 2').get().val(),
        'price':db.child('Data').child('Price').child('Day').get().val(),
        'img':db.child('Data').child('Image').child('Day 2').get().val()
        },
        'Day3':{
        'date':db.child('Data').child('Date').child('Day 3').get().val(),
        'price':db.child('Data').child('Price').child('Normal').get().val(),
        'img':db.child('Data').child('Image').child('Normal').get().val()
        },
            

    }
    
    return render(request,"home.html",{'context':context})
    

def otp(request):
    return render(request, "main/otp.html")

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
        doc_ref = db.collection('all_otps').document()

        doc_ref.set({
            'id': doc_ref.id,
            'email': email,
            'otp': otp,
        })
        request.session['OTPId'] = doc_ref.id
        
    except Exception as e:
        print(e)
    return JsonResponse({"otp": "otp"})


def verify_otp(request):
    # Get the list of OTP values from the POST data
    otp_values = request.POST.getlist('otp')
    # Combine the OTP values into a single string
    otp = ''.join(otp_values)

    otpID = request.session.get('OTPId')
    snapshots = db.collection('all_otps').where('id', '==', otpID).stream() #
    users = []
    otp1 = 0
    for user in snapshots:
        formattedData = user.to_dict()
        print(formattedData)
        otp1 = formattedData['otp']
        users.append(user.reference)

    OTP = int(otp)
    print(OTP, otp1)
    if OTP == otp1:
        return redirect('register')
    
    email = request.session.get('LeaderEmail')
    context = {
        'message': "Incorrect OTP",
        'email': email
    }
    return render(request, 'main/otp.html', context)


def register(request):
    email = request.session.get('LeaderEmail')
    return render(request, 'main/register.html', {'email': email})





def Order_Summary(request):
    Todata = request.session.get('Todata', {})
    members = request.session.get('members', {})
    form_data = request.session.get('form_data', {})
    return render(request, 'main/Order_Summary.html',{'form_data': form_data,'members':members,"tdata":Todata})

def unique_id(length):
    while True:
        random_string = ''.join(random.choices(string.ascii_letters + string.digits, k=length))
        if random_string not in used_strings:
            used_strings.add(random_string)
            return random_string
used_strings = set()
def savedata(request):
    price={
        'NORMAL': 500,
        'VIP': 750,
        'SUPER_VIP': 850,
    }
    if request.method == 'POST':
        id = unique_id(5)
        amount = 750
        status="Pending"
        err_des={
            'error':0,
            'pass':1,
        }
        # fee_id = "M1006"
        paases_type = {
            'NORMAL': 0,
            'VIP': 0,
            'SUPER VIP': 0,
            'amount': 0,
        }
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
        if (Lpasstype == 'NORMAL'):
            paases_type['NORMAL'] = paases_type['NORMAL']+1
        elif (Lpasstype == 'VIP'):
            paases_type['VIP'] = paases_type['VIP']+1
        elif (Lpasstype == 'SUPER VIP'):
            paases_type['SUPER VIP'] = paases_type['SUPER VIP']+1
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
        doc_ref = db.collection('transaction').document(id)
        doc_ref.set(Tdata)
        doc_ref.collection('users').document().set(Ldata)
        length = {len(membernames)}
        members=[]
        for i in range(len(membernames)):
            member = {
                "name": membernames[i],
                "contact": member_contacts[i],
                "gender": member_gender[i],
                "pass_type": member_passtype[i],
                "id_type": member_idtype[i],
                "id_number": member_idnumber[i],
                "age": member_age[i],
                'email': member_email[i],
            }
            if (member_passtype[i] == 'NORMAL'):
                paases_type['NORMAL'] = paases_type['NORMAL']+1
            elif (member_passtype[i] == 'VIP'):
                paases_type['VIP'] = paases_type['VIP']+1
            elif (member_passtype[i] == 'SUPER VIP'):
                paases_type['SUPER VIP'] = paases_type['SUPER VIP']+1
            doc_ref.collection('users').document().set(member)
            members.append(member)
        amount = paases_type['NORMAL']*500 + (paases_type['VIP']*750)+(paases_type['SUPER VIP'])*850
        Todata = {
            "Email": LeaderEmail,
            # "time":time,
            "amount":amount,
            "err_des":err_des,
            "status":status,
            
        }
        request.session.flush()
        request.session['members']=members
        request.session['Todata'] = Todata
        request.session['form_data'] = request.POST
        return redirect(Order_Summary)
    form_data = request.session.get('form_data', {})
    members = request.session.get('members', {})
    Todata = request.session.get('Todata', {})
    return render(request, 'main/register.html', {'form_data': form_data,'members':members,"tdata":Todata,"price":price})