from django.shortcuts import render

# Create your views here.
def Success(request):
    return render(request, "payment/success.html")