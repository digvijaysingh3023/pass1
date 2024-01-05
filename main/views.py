from django.shortcuts import render
from . models import Pass

# Create your views here.
def home(request):
    passes=Pass.objects.all()
    return render(request,"home.html",{'passes':passes})

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