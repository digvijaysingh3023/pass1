from django.shortcuts import render
from . models import Pass
from django.core.mail import EmailMessage
from django.core.mail import send_mail
import random
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
    return render(request,"home.html",{'passes':passes, 'name': name})

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

    return render(request, 'order_summary.html', {'transactions': transactions})