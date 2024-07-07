from django.urls import path
from . import views

app_name = 'Home'

urlpatterns = [
    path('', views.index, name='home'),
    path('aboutus', views.aboutus, name="aboutus"),
    path('privacypolicy', views.privacy_policy, name="privacy_policy"),
    path('termsofservice', views.terms_of_service, name="terms_of_service"),
    path('contact', views.contactus, name='contact')
]
