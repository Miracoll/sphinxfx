from django.shortcuts import render
from django.core.mail import send_mail, EmailMultiAlternatives
from django.conf import settings
from django.contrib import messages
from super.models import Contact
from account.functions import telegram

# Create your views here.

def home(request):
    context = {}
    return render(request, 'fronpage/index.html', context)

def contact(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        mobile = request.POST.get('mobile')
        subject = request.POST.get('subject')
        message = request.POST.get('message')
        
        # Send message to admin
        telegram(f'Hello admin, you have a message from {name} (unregistered user).\n{message}\n{email}\n{mobile}\n{subject}')
        messages.success(request, 'sent')
        
    context = {}
    return render(request, 'fronpage/contactus.html', context)

def doge(request):
    context = {}
    return render(request, 'fronpage/dogemining.html', context)

def bitcoin(request):
    context = {}
    return render(request, 'fronpage/bitcoinmining.html', context)

def aboutMining(request):
    context = {}
    return render(request, 'fronpage/aboutmining.html', context)

def responsibleTrading(request):
    context = {}
    return render(request, 'fronpage/responsibletrading.html', context)

def whatIsLeverage(request):
    context = {}
    return render(request, 'fronpage/whatisleverage.html', context)

def copyExpertTrades(request):
    context = {}
    return render(request, 'fronpage/copyexperttraders.html', context)

def optionsTrading(request):
    context = {}
    return render(request, 'fronpage/optionstrading.html', context)

def cryptoTrading(request):
    context = {}
    return render(request, 'fronpage/cryptotrading.html', context)

def stockTrading(request):
    context = {}
    return render(request, 'fronpage/stocktrading.html', context)

def forexTrading(request):
    context = {}
    return render(request, 'fronpage/forextrading.html', context)

def generalRisk(request):
    context = {}
    return render(request, 'fronpage/generalrisk.html', context)

def termOfService(request):
    context = {}
    return render(request, 'fronpage/termsofservice.html', context)

def privacyPolicy(request):
    context = {}
    return render(request, 'fronpage/privacypolicy.html', context)

def cookie(request):
    context = {}
    return render(request, 'fronpage/cookie.html', context)

def about(request):
    context = {}
    return render(request, 'fronpage/aboutus.html', context)