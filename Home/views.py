from django.shortcuts import render, redirect
from Publisher.models import *
from .models import *
from django.core.mail import send_mail

def index(request):
    # Fetch featured apps, games, and ebooks from the database
    featured_apps = App.objects.filter()[:6]
    featured_games = Game.objects.filter()[:6]
    featured_ebooks = eBook.objects.filter()[:6]

    context = {
        'featured_apps': featured_apps,
        'featured_games': featured_games,
        'featured_ebooks': featured_ebooks,
    }
    return render(request, 'index.html', context)

def aboutus(request):
    return render(request, 'aboutus.html')
    
def privacy_policy(request):
    return render(request, 'privacy_policy.html')

def terms_of_service(request):
    return render(request, 'terms_of_service.html')

def contactus(request):
    if request.method == 'POST':
        contact_name = request.POST.get('contactName')
        contact_email = request.POST.get('contactEmail')
        contact_subject = request.POST.get('contactSubject')
        contact_message = request.POST.get('contactMessage')

        # Validate form data
        if contact_name and contact_email and contact_subject and contact_message:
            # Save the form data to the database
            ContactUs.objects.create(
                name=contact_name,
                email=contact_email,
                subject=contact_subject,
                message=contact_message,
            )

            # Send an email (you can customize this part)
            subject = f'Query Recieved'
            message = f'Hi {contact_name}, Thank You for contacting Us..'
            from_email = settings.EMAIL_HOST_USER
            recipient_list = [contact_email]
            send_mail(subject, message, from_email, recipient_list)

            # Redirect to a success page or render a success message
            return redirect('/#contact')
    return render(request, 'index.html#contact')