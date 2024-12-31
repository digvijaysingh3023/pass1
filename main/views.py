from django.shortcuts import render,redirect
from django.http import JsonResponse
# from .models import Pass
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.core.mail import EmailMessage
from django.core.mail import send_mail
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
# from .encrypt_decrypt import encrypt
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
from fpdf import FPDF
import qrcode
from io import BytesIO
import pandas as pd
@api_view(['GET'])
def user_data(request):
    try:
        email = request.query_params.get('Email', None)
        if not email:
            return Response({'error': 'Email is required'}, status=status.HTTP_400_BAD_REQUEST)
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
if not firebase_admin._apps:
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
    return JsonResponse(data2)

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
    return JsonResponse({"otp": otp})


def verify_otp(request):
    # Get the list of OTP values from the POST data
    otp_values = request.POST.getlist('otp')
    # Combine the OTP values into a single string
    otp = ''.join(otp_values)
    otpID = request.session.get('OTPId')
    snapshots = db.collection('all_otps').where('id', '==', otpID).stream() #
    users = []
    otp1 = 100000
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
    cod = request.session.get('cod', {})
    members = request.session.get('members', {})
    form_data = request.session.get('form_data', {})
    return render(request, 'main/Order_Summary.html',{'form_data': form_data,'members':members,"tdata":Todata,"cod":cod})

def unique_id(length):
    iv = (db.collection('transaction').stream())
    document_ids = [doc.id for doc in iv]
    while True:
        random_string = ''.join(random.choices(string.ascii_letters + string.digits, k=length))
        if random_string not in document_ids:
            print(random_string)
            return random_string

# @login_required(login_url="otp")
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
        print(LeaderContact_no)
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
        cod = request.POST.getlist('code')
        print(cod)
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
            "LContact": cod[0]+LeaderContact_no,
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
                "contact": cod[i+1]+member_contacts[i],
                "gender": member_gender[i],
                "pass_type": member_passtype[i],
                "id_type": member_idtype[i],
                "id_number": member_idnumber[i],
                "age": member_age[i],
                'email': member_email[i],
            }
            print(member['contact'])
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
        request.session['cod'] = cod[0]
        request.session['form_data'] = request.POST
        return redirect(Order_Summary)
    email = request.session.get('LeaderEmail',{})
    form_data = request.session.get('form_data', {})
    members = request.session.get('members', {})
    Todata = request.session.get('Todata', {})
    return render(request, 'main/register.html', {'form_data': form_data,'members':members,"tdata":Todata,"prices":prices[0] , "passtype" : pass_types[0], "leadermail" : email})

from .encrypt import encrypt
import requests

def payment(request):
    mess= encrypt('KHohdmJKjnAQ4NahuaoQBw==',"1000602|DOM|IN|INR|1|NA|https://alcheringa.in|https://rocko.alcheringa.in|SBIEPAY|003001|003001|NB|ONLINE|ONLINE","SHA256")
    print(mess)
    url = "https://test.sbiepay.sbi"
    payload = {
        'EncryptTrans': mess
    }
    response = requests.post(url, data=payload,headers={'Content-Type': 'text/html'})
    print(response.text)
    return HttpResponse(response)
# payment(1)

def passes(request):
    try:
        if request.user.is_authenticated:
            user_email = request.session.get('LeaderEmail', {})
            passes_info = []
            user_ref = db.collection('transaction').where('Email', '==', user_email).stream()
            for transaction in user_ref:
                transaction_data = transaction.to_dict()
                users = transaction_data.get('users', {})
                for user_id, user_info in users.items():
                    pass_type = user_info.get('pass_type', '')

                    if pass_type:
                        passes_info.append({
                            'user_id': user_id,
                            'pass_type': pass_type,
                        })
            pdf = generate_pdf(passes_info)
            response = HttpResponse(pdf, content_type='application/pdf')
            response['Content-Disposition'] = 'attachment; filename="passes.pdf"'
            return response
        else:
            return HttpResponse("User is not authenticated.")

    except Exception as e:
        print(e)
        return HttpResponse("An error occurred.")


def export_verified_users_to_excel(request):
    try:
        # Fetch all verified users from Firestore
        verified_users_ref = db.collection('verified_user').stream()
        verified_users = [user.to_dict() for user in verified_users_ref]

        # Create a DataFrame from the verified users data
        df = pd.DataFrame(verified_users)

        # Create an Excel writer object and write the DataFrame to an Excel file
        output = BytesIO()
        writer = pd.ExcelWriter(output, engine='xlsxwriter')
        df.to_excel(writer, index=False, sheet_name='Verified Users')
        writer.book.close()  # Close the workbook to save it
        output.seek(0)

        # Create an HTTP response with the Excel file
        response = HttpResponse(output, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename=verified_users.xlsx'
        return response

    except Exception as e:
        print(e)
        return HttpResponse("An error occurred while exporting data to Excel.")
def generate_pdf(pass_type):
    pdf = FPDF('L', 'mm', (270, 870))
    pdf.add_page()
    if pass_type == 'ebsp':
        pdf.image("images/EBSP.png", 0, 0, pdf.w, pdf.h)
    elif pass_type == 'nsp':
        pdf.image("images/NSP.png", 0, 0, pdf.w, pdf.h)
        qr_code_data = 'https://www.example.com/' + pass_data['pass_id']
        aztec = qrcode.QRCode(version=1, box_size=10, border=4)
        aztec.add_data(qr_code_data)
        aztec.make(fit=True)
        if pass_type == 'ebsp':
           aztec_img = aztec.make_image(fill_color="white", back_color="#677DE0")
        elif pass_type == 'nsp':
           aztec_img = aztec.make_image(fill_color="white", back_color="#F28E15")
        qr_code_path = f'aztec_code_{pass_data["pass_id"]}.png'
        aztec_img.save(qr_code_path)
        aztec_img = aztec_img.resize((85, 85))
        pdf.image('aztec_code.png', pdf.w - 365, pdf.h - 230, 150, 150)
        pdf.add_page()
        pdf.image("images/BoardPassBack2.png", 0, 0, pdf.w, pdf.h)

    output = BytesIO()
    pdf.output(output)
    return qr_code_image_path

# def automation(request):
    index=db.collection('index').document('rcT6Wb8kyh07erua4VaM').get().to_dict()['index']
    data=pd.read_excel(r'/Users/shivamg/Downloads/Book1.xlsx')
    pendinguser=db.collection('pending_user').stream()
    pend=[]
    for puser in pendinguser:
        user=puser.to_dict()
        ind = user['index']
        if data['PAYMENT_STATUS'][ind]== 'SUCCESS':
            verified = db.collection('verified_user').document()
            email=data['EMAIL'][ind]
            verify={
                "name": data['FIRST_NAME'][ind] + " " + data['LAST_NAME'][ind],
                "gender": data['GENDER'][ind],
                "contact no.":data['PHONE_NUMBER'][ind],
                "email":data['EMAIL'][ind],
                "Booking id":data['BOOKING_ID'][ind],
                "payment_status":data['PAYMENT_STATUS'][ind],
                "Amount":data['AMOUNT_PAID'][ind],
            }
            verified.set(verify)
            subject = 'just for testing'
            message='you have been verified'
            from_email = settings.EMAIL_HOST_USER
            send_mail(subject, message, from_email, [email])
        pend.append(user)
        
    for i in range(index,len(data)):
        if data['PAYMENT_STATUS'][i]== 'SUCCESS':
            verified = db.collection('verified_user').document()
            email=data['EMAIL'][i]
            verify={
                "name": data['FIRST_NAME'][i] + " " + data['LAST_NAME'][i],
                "gender": data['GENDER'][i],
                "contact no.":data['PHONE_NUMBER'][i],
                "email":data['EMAIL'][i],
                "Booking id":data['BOOKING_ID'][i],
                "payment_status":data['PAYMENT_STATUS'][i],
                "Amount":data['AMOUNT_PAID'][i],
            }
            verified.set(verify)
            subject = 'just for testing'
            message='you have been verified'
            from_email = settings.EMAIL_HOST_USER
            send_mail(subject, message, from_email, [email])
            index+=1
        if data['PAYMENT_STATUS'][i]== 'PENDING':
            pendings = db.collection('pending_user').document()
            pending={
                "name": data['FIRST_NAME'][i] + " " + data['LAST_NAME'][i],
                "gender": data['GENDER'][i],
                "contact no.":data['PHONE_NUMBER'][i],
                "email":data['EMAIL'][i],
                "Booking id":data['BOOKING_ID'][i],
                "payment_status":data['PAYMENT_STATUS'][i],
                "Amount":data['AMOUNT_PAID'][i],
                "index":i,
            }
            pendings.set(pending)
    db.collection('index').document('rcT6Wb8kyh07erua4VaM').update({'index':index})

    return index
# print(automation(1))