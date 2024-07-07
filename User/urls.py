from django.urls import path
from . import views

app_name = 'User'

urlpatterns = [
    path('', views.user_home, name='user_home'),
    path('login/', views.login, name='user_login'),
    path('login_with_otp/', views.login_with_otp, name='user_login_with_otp'),
    path('verify_login_otp/', views.verify_login_otp, name='user_verify_login_otp'),
    path('signup/', views.signup, name='user_signup'),
    path('forgot_password/', views.forgot_password, name='user_forgot_password'),
    path('verify_otp/', views.verify_otp, name='user_verify_otp'),
    path('change_password/', views.change_password, name='user_change_password'),
    path('logout/', views.logout, name='logout'),
    path('account_settings/', views.account_settings, name='account_settings'),
   path('verify_update_otp/<str:action>/', views.verify_update_otp, name='verify_update_otp'),
    path('browse_apps/', views.browse_apps, name='browse_apps'),
    path('browse_games/', views.browse_games, name='browse_games'),
    path('browse_ebooks/', views.browse_ebooks, name='browse_ebooks'),
    path('content_detail/<str:content_type>/<int:content_id>/', views.content_detail, name='content_detail'),
    path('<str:content_type>/purchase/<int:content_id>/', views.process_purchase, name='process_purchase'),
    path('<str:content_type>/download/<int:content_id>/', views.content_download, name='content_download'),
    path('my_library/', views.my_library, name='my_library'),
    path('review/<int:content_id>/', views.submit_review, name='review_submit'),
]
