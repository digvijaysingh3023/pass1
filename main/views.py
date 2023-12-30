from django.shortcuts import render
from . models import Pass

# Create your views here.
def home(request):
    passes=Pass.objects.all()
    return render(request,"home.html",{'passes':passes})