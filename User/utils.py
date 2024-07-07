import random
from django.core.mail import send_mail
from django.conf import settings
from django.conf.urls.static import static

def generate_otp():
    otp = ''.join(random.choices('0123456789', k=6))
    return otp

def send_otp_email(email, otp, text):
    subject = f'{text} OTP'
    message = f'Your OTP for {text} is: {otp}'
    from_email = settings.EMAIL_HOST_USER
    recipient_list = [email]
    send_mail(subject, message, from_email, recipient_list)