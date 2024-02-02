from django.shortcuts import render,redirect
from django.http import JsonResponse
# from .models import Pass
from django.core.mail import EmailMessage
from django.core.mail import send_mail
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from .encrypt_decrypt import encrypt
from django.utils import timezone
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
import random
import string
import random
import json
# import status
import pyrebase 
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
from django.contrib.auth.decorators import login_required
from Crypto.Protocol.KDF import PBKDF2

@api_view(['GET'])
def user_data(request):
    try:
        email = request.query_params.get('Email', None)
        print
        if not email:
            return Response({'error': 'Email is required'}, status=status.HTTP_400_BAD_REQUEST)
        print(213124)
        users=[]
        user_ref = db.collection('transaction').where('Email','==',email).stream()
        print(email)
        for user in user_ref:
            user_dic = user.to_dict()
            print(user_dic['Email'])
            users.append(user_dic)
        if not users:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        user = users[0]
        has_passes=user['err_des']['pass']
        print(has_passes+100)
        if has_passes:
            # Encrypt user data as needed
            salt=b'\xb9{>\n)O&;\xc0\\\xd7C\xd9\xe6\x8e\x004\xd6\x8c\x0c\xb8\x83\xb2\x8f\xd7\x0f\x1a\xd7M\x12\xb4a'
            key = PBKDF2("password",salt,dkLen=32)
            encrypted_data = encrypt(key,user)
        return Response(encrypted_data)
        # else:
        #     return Response({'error': 'User has no passes'}, status=status.HTTP_404_NOT_FOUND)

    except Exception as e:
        print(e)
        return Response({'error': 'An error occurred'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

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

def get_data(request):
    data1 = {
        'DAY 1': db.collection('Data').document('Day-1').get().to_dict(),
        'DAY 2': db.collection('Data').document('Day-2').get().to_dict(),
        'DAY 3': db.collection('Data').document('Day-3').get().to_dict(),
    }
    data2 = {
        'EARLY BIRD SEASON PASS': db.collection('Data').document('EARLY BIRD SEASON PASS').get().to_dict(),
        'NORMAL SEASON PASS': db.collection('Data').document('NORMAL SEASON PASS').get().to_dict(),
    }
    request.session['dayWisePasses'] = data1
    request.session['seasonPasses'] = data2
    return JsonResponse(data1)

def home(request):
    dayWisePasses = request.session.get('dayWisePasses', {})
    print(dayWisePasses)
    seasonPasses = request.session.get('seasonPasses', {})
    return render(request, "main/home.html",{'dayWisePasses': dayWisePasses,'seasonPasses':seasonPasses})
    

def otp(request):
    return render(request, "main/otp.html")

def Success(request):
    return render(request, "main/success.html")

@csrf_exempt
def sendOtp(request):
    try:
        email = json.loads(request.body)['email']
        request.session['LeaderEmail'] = email
        otp = random.randint(100000, 999999)
        print("OTP : ", otp)
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



price=db.collection('price').stream()
prices = []
for doc in price:
    x = doc.to_dict()
    prices.append(x)
for pr in x:
    print((x[pr]))

def Order_Summary(request):
    Todata = request.session.get('Todata', {})
    members = request.session.get('members', {})
    form_data = request.session.get('form_data', {})
    return render(request, 'main/Order_Summary.html',{'form_data': form_data,'members':members,"tdata":Todata})

def unique_id(length):
    iv = (db.collection('transaction').stream())
    document_ids = [doc.id for doc in iv]
    while True:
        random_string = ''.join(random.choices(string.ascii_letters + string.digits, k=length))
        if random_string not in document_ids:
            print(random_string)
            return random_string
used_strings = set()

# @login_required
def savedata(request):
    price=db.collection('price').stream()
    prices = []
    for doc in price:
        x = doc.to_dict()
        prices.append(x)
    passt = db.collection('pass_type').stream()
    pass_types =[]
    for doc in passt:
        y=doc.to_dict()
        pass_types.append(y)
    
    if request.method == 'POST':
        id = unique_id(5)
        # amount = 750
        status="Pending"
        err_des={
            'error':0,
            'pass':1,
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
        amount=0
        pas=pass_types[0]
        for i in range(1,len(y)+1):
            if(Lpasstype == pas[str(i)]):
                amount+=x[pas[str(i)]]
        member_email = request.POST.getlist('email')
        Tdata = {
            "Email": LeaderEmail,
            "time":time,
            "amount":amount,
            "err_des":err_des,
            "status":status,
            
        }
        Ldata={
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
            for j in range(1,len(y)+1):
                if(member_passtype[i] == pas[str(j)]):
                    amount+=x[pas[str(j)]]
            doc_ref.collection('users').document().set(member)
            members.append(member)
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
    email = request.session.get('LeaderEmail',{})
    form_data = request.session.get('form_data', {})
    members = request.session.get('members', {})
    Todata = request.session.get('Todata', {})
    return render(request, 'main/register.html', {'form_data': form_data,'members':members,"tdata":Todata,"prices":prices[0] , "passtype" : pass_types[0], "leadermail" : email})