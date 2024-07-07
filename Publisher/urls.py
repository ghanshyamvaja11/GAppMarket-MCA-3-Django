from django.urls import path
from . import views

app_name = 'Publisher'

urlpatterns = [
    path('', views.publisher_home, name='publisher_home'),
    path('login/', views.login, name='publisher_login'),
    path('login_with_otp/', views.login_with_otp, name='publisher_login_with_otp'),
    path('verify_login_otp/', views.verify_login_otp, name='publisher_verify_login_otp'),
    path('signup/', views.signup, name='publisher_signup'),
     path('forgot_password/', views.forgot_password, name='publisher_forgot_password'),
    path('verify_otp/', views.verify_otp, name='publisher_verify_otp'),
    path('change_password/', views.change_password, name='publisher_change_password'),
    path('logout/', views.logout, name='logout'),
    path('account_settings/', views.account_settings, name='account_settings'),
    path('verify_update_otp/<str:action>/', views.verify_update_otp, name='verify_update_otp'),
     path('dashboard/', views.publisher_dashboard, name='publisher_dashboard'),
    path('my_content/', views.publisher_my_content, name='publisher_my_content'),
    path('my_content/<int:content_id>/edit/', views.publisher_edit_content, name='publisher_edit_content'),
    path('<str:content_type>/download/<int:content_id>/', views.content_download, name='content_download'),
    path('my_content/<int:content_id>/delete/', views.publisher_delete_content, name='publisher_delete_content'),
    path('upload/', views.publisher_upload, name='publisher_upload'),
    path('sales_reports/', views.publisher_sales_reports, name='sales_reports'),
    path('publisher/reviews/', views.publisher_reviews, name='publisher_reviews'),
]
