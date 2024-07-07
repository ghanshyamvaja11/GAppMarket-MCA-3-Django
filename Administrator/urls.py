from django.urls import path
from . import views

app_name = 'Administrator'

urlpatterns = [
    path('', views.administrator_home, name='admin_home'),
    path('login/', views.login, name='admin_login'),
    path('login_with_otp/', views.login_with_otp, name='admin_login_with_otp'),
    path('verify_login_otp/', views.verify_login_otp, name='admin_verify_login_otp'),
    path('signup/', views.signup, name='admin_signup'),
     path('forgot_password/', views.forgot_password, name='admin_forgot_password'),
    path('verify_otp/', views.verify_otp, name='admin_verify_otp'),
    path('change_password/', views.change_password, name='admin_change_password'),
    path('logout/', views.logout, name='logout'),
    path('account_settings/', views.account_settings, name='account_settings'),
    path('verify_update_otp/<str:action>/', views.verify_update_otp, name='verify_update_otp'),
     path('contact_management/', views.contactus, name='contact_management'),
    path('send_email/<int:query_id>/', views.send_contact_query_email, name='send_contact_query_email'),
    path('user_management/', views.user_management, name='user_management'),
    path('block_user/<int:user_id>/', views.block_user, name='block_user'),
    path('unblock_user/<int:user_id>/', views.unblock_user, name='unblock_user'),
    path('delete_user/<int:user_id>/', views.delete_user, name='delete_user'),
    path('publisher_management/', views.publisher_management, name='publisher_management'),
    path('publisher_management/block/<int:publisher_id>/', views.block_publisher, name='block_publisher'),
    path('publisher_management/unblock/<int:publisher_id>/', views.unblock_publisher, name='unblock_publisher'),
    path('publisher_management/delete/<int:publisher_id>/', views.delete_publisher, name='delete_publisher'),
    path('content_management/', views.content_management, name='content_management'),
    path('content_management/block/<int:content_id>/', views.block_content, name='block_content'),
    path('content_management/unblock/<int:content_id>/', views.unblock_content, name='unblock_content'),
    path('content_management/delete/<int:content_id>/', views.delete_content, name='delete_content'),
    path('announcements/', views.admin_announcements, name='admin_announcements'),
]
