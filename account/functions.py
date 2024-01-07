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