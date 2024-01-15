from django.contrib import messages
from django.template.loader import render_to_string
from django.contrib.sites.shortcuts import get_current_site
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.core.mail import EmailMessage
from django.shortcuts import redirect
from django.core.mail import send_mail, EmailMultiAlternatives
from .tokens import account_activation_token
import requests
import json
import socket
from datetime import datetime

def activateEmail(request, user, to_email):
    mail_subject = 'Account verification'
    message = render_to_string('account/activate.html', {
        'user':user.username,
        'email':to_email,
        'domain':get_current_site(request).domain,
        'uid':urlsafe_base64_encode(force_bytes(user.pk)),
        'token':account_activation_token.make_token(user),
        'protocol':'https' if request.is_secure else 'http'
    }
    )
    # email = EmailMessage(mail_subject, message, to=[to_email])
    email = EmailMultiAlternatives(mail_subject, message, to=[to_email])
    email.attach_alternative(message, "text/html")
    email.content_subtype = 'html'
    email.send()
    if email.send():
        messages.success(request, f'A verification mail has been sent to {to_email}, pls verify before login')
    else:
        messages.error(request, f'Problem sending email to {to_email}, please try again')
        
def telegram(message):
    TOKEN = "6212231441:AAG3CH9XlsSPDodsBkSZo1kNEhbVwh5cbYo"
    chat_id = "5471999533"
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage?chat_id={chat_id}&text={message}"
    requests.get(url)
    
def adminAlert(request,message):
    # hostname = socket.gethostname()
    # ip_address = socket.gethostbyname(hostname)
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    current_datetime = datetime.now()
    url = "https://app.smartsmssolutions.com/io/api/client/v1/sms/"
    payload={'token': '7pHQVZ1NY1LmG3piWKNdnlh7Mj30wBeUZ7jJupCOq3dyPr3H8W',
    'sender': 'RRR',
    'to': '09066349701',
    'message': f'SPHINXFX NOTICE\n{message}.\nIP Address:{ip}\nDate:{current_datetime}',
    'type': 0,
    'routing': 3,
    }
    files=[]
    headers = {}
    response = requests.request("POST", url, headers=headers, data=payload, files=files)
    print(response.text)
    
    
    # message = f'SPHINXFX NOTICE\n{message}.\nIP Address:{ip}\nDate:{current_datetime}'
    # msg = message.replace(' ','+')
    # url = f'https://api.callmebot.com/whatsapp.php?phone=2348171270502&text={msg}&apikey=2600741'
    # x = requests.post(url)
    
    
    # print(res.get('units_after'))
    # if int(res.get('units_after')) <= 50:
    #     message = 'SPHINXFX SMS unit is running  low, top up now'
    #     msg = message.replace(' ','+')
    #     url = f'https://api.callmebot.com/whatsapp.php?phone=2348171270502&text={msg}&apikey=2600741'
    #     x = requests.post(url)
    
    