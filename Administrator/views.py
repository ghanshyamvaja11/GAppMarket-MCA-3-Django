from django.shortcuts import render, get_object_or_404
from django.contrib.auth import authenticate, login as auth_login
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from .models import *
from django.contrib.auth.hashers import make_password
from .utils import generate_otp, send_otp_email
from django.core.mail import send_mail
from django.contrib.auth.backends import ModelBackend
from Publisher.models import *
from User.models  import *
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from Home.models import ContactUs
from django.contrib.auth import logout as auth_logout
import os

@login_required(login_url='/administrator/login')
def administrator_home(request):
    # Fetch necessary data for the dashboard
    total_users = User.objects.count()
    total_publishers = Publisher.objects.count()
    total_content = Content.objects.count()

    context = {
        'total_users': total_users,
        'total_publishers': total_publishers,
        'total_content': total_content,
    }
    return render(request, 'Administrator/admin_home.html', context)

def contactus(request):
    queries = ContactUs.objects.all()  # Fetch all queries from database
    context = {
        'queries': queries
    }
    return render(request, 'Administrator/contact_management.html', context)

def send_contact_query_email(request, query_id):
    query = get_object_or_404(ContactUs, id=query_id)

    if request.method == 'POST':
        email_message = request.POST.get('email_message')

        send_mail(
            f"Response to your query: {query.subject}",
            email_message,
            settings.EMAIL_HOST_USER,
            [query.email],  # send to the query submitter
            fail_silently=False,
        )

         # Delete the query after sending the email
        query.delete()
        
        return redirect('Administrator:contact_management')  # Redirect back to contact management page

    return redirect('Administrator:contact_management')

def login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            auth_login(request, user)
            request.session['UserType'] = 'Administrator'
            return redirect('Administrator:admin_home')  # Redirect tAdministrator:o admin dashboard after login
        else:
            # Handle invalid login
            return render(request, 'Administrator/login.html', {'error_message': 'Invalid username or password.'})
    else:
        return render(request, 'Administrator/login.html')

def logout(request):
    auth_logout(request)
    return redirect('Administrator:admin_login')
    
def signup(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        hashed_password = make_password(password)  # Hash the password before saving
        
        # Create a new Administrator object
        new_admin = Administrator(username=username, email=email, password=hashed_password)
        new_admin.save()

        # Redirect tAdministrator:o login page after successful signup
        return redirect('Administrator:admin_login')
    else:
        return render(request, 'Administrator/signup.html')

def login_with_otp(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        try:
            admin = Administrator.objects.get(email=email)
        except Administrator.DoesNotExist:
            return render(request, 'Administrator/login_with_otp.html', {'error_message': 'No administrator found with this email.'})
        
        otp = generate_otp()
        send_otp_email(email, otp, 'login with OTP')
        request.session['login_email'] = email
        request.session['login_otp'] = otp
        return redirect('Administrator:admin_verify_login_otp')
    else:
        return render(request, 'Administrator/login_with_otp.html')

def verify_login_otp(request):
    if request.method == 'POST':
        entered_otp = request.POST.get('otp')
        saved_otp = request.session.get('login_otp')
        if entered_otp == saved_otp:
            email = request.session.get('login_email')
            admin = Administrator.objects.get(email=email)
            # Explicitly set the authentication backend
            Administrator.backend = f"{Administrator._meta.app_label}.{ModelBackend.__name__}"
            auth_login(request, admin)
            return redirect('Administrator:admin_home')
        else:
            return render(request, 'Administrator/verify_login_otp.html', {'error_message': 'Invalid OTP.'})
    else:
        return render(request, 'Administrator/verify_login_otp.html')

def forgot_password(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        try:
            user = Administrator.objects.get(email=email)
        except Administrator.DoesNotExist:
            return render(request, 'Administrator/forgot_password.html', {'error_message': 'No administrator found with this email.'})
        
        otp = generate_otp()
        send_otp_email(email, otp, 'forgot password')
        request.session['reset_email'] = email
        request.session['reset_otp'] = otp
        return redirect('Administrator:admin_verify_otp')
    else:
        return render(request, 'Administrator/forgot_password.html')

def verify_otp(request):
    if request.method == 'POST':
        entered_otp = request.POST.get('otp')
        saved_otp = request.session.get('reset_otp')
        if entered_otp == saved_otp:
            return redirect('Administrator:admin_change_password')
        else:
            return render(request, 'Administrator/verify_otp.html', {'error_message': 'Invalid OTP.'})
    else:
        return render(request, 'Administrator/verify_otp.html')

def change_password(request):
    if request.method == 'POST':
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')
        if new_password == confirm_password:
            email = request.session.get('reset_email')
            user = Administrator.objects.get(email=email)
            user.set_password(new_password)
            user.save()
            return redirect('Administrator:admin_login')
        else:
            return render(request, 'Administrator/change_password.html', {'error_message': 'Passwords do not match.'})
    else:
        return render(request, 'Administrator/change_password.html')

def account_settings(request):
    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'saveChanges':
            # Regular account settings update
            first_name = request.POST.get('first_name')
            last_name = request.POST.get('last_name')
            new_email = request.POST.get('new_email')
            new_password = request.POST.get('new_password')
            
            user = request.user
            
            if new_email:
                old_email = user.email
                request.session['new_email'] = new_email  # Store new email in session
                
                # Send OTP to the old email for verification
                otp_code = generate_otp()
                request.session['account_changes_otp'] = otp_code  # Store OTP in session
                
                # Send OTP via email
                send_otp_email(old_email, otp_code, 'Email Change')
                
                # Redirect tAdministrator:o OTP verification page
                return redirect('Administrator:verify_update_otp', action='email_change')
            
            elif new_password:
                # Change password without OTP verification
                user.set_password(new_password)
                user.save()
                
                # Update session authentication hash to prevent logging out
                update_session_auth_hash(request, user)
                
                messages.success(request, 'Password changed successfully.')
                return redirect('Administrator:account_settings')

            else:
                # No changes made, display old data
                messages.info(request, 'No changes made.')
                return render(request, 'Administrator/account_settings.html', {'user': user})
        
    return render(request, 'Administrator/account_settings.html', {'user': request.user})

def verify_update_otp(request, action):
    if request.method == 'POST':
        entered_otp = request.POST.get('otp')
        saved_otp = request.session.get('account_changes_otp')
        
        if entered_otp == saved_otp:
            if action == 'email_change':
                # Apply email change
                new_email = request.session.get('new_email')
                user = request.user
                user.email = new_email
                user.save()
                
                # Clear OTP session data
                del request.session['account_changes_otp']
                del request.session['new_email']
                messages.success(request, 'Email changed successfully.')
                return redirect('Administrator:account_settings')
            # Add more actions if needed
            
        else:
            messages.error(request, 'Invalid OTP. Please try again.')

    return render(request, 'Administrator/verify_otp.html', {'action': action})

@login_required(login_url='/administrator/login')
def user_management(request):
    query = request.GET.get('q')
    users = User.objects.all()

    if query:
        users = users.filter(
            username__icontains=query  # Adjust to the actual field you want to search
        )

    return render(request, 'Administrator/user_management.html', {'users': users, 'search_query': query})

@login_required(login_url='/administrator/login')
def block_user(request, user_id):
    user = get_object_or_404(User, id=user_id)
    if request.method == 'POST':
        user.is_active = False
        user.save()
        # Send email notification
        send_email_notification(user.email, 'User Blocked', f'{user.username} has been blocked.')
        messages.success(request, f'{user.username} has been blocked.')
        return redirect('Administrator:user_management')
    return render(request, 'Administrator/block_user.html', {'user': user})

@login_required(login_url='/administrator/login')
def unblock_user(request, user_id):
    user = get_object_or_404(User, id=user_id)
    if request.method == 'POST':
        user.is_active = True
        user.save()
        # Send email notification
        send_email_notification(user.email, 'User Unblocked', f'{user.username} has been unblocked.')
        messages.success(request, f'{user.username} has been unblocked.')
        return redirect('Administrator:user_management')
    return render(request, 'Administrator/unblock_user.html', {'user': user})

@login_required(login_url='/administrator/login')
def delete_user(request, user_id):
    user = get_object_or_404(User, id=user_id)
    if request.method == 'POST':
        # Send email notification before deletion
        send_email_notification(user.email, 'User Deleted', f'{user.username} has been deleted.')
        user.delete()
        messages.success(request, f'{user.username} has been deleted.')
        return redirect('Administrator:user_management')
    return render(request, 'Administrator/delete_user.html', {'user': user})

@login_required(login_url='/administrator/login')
def publisher_management(request):
    query = request.GET.get('q')
    publishers = Publisher.objects.all()

    if query:
        publishers = publishers.filter(
            username=query  # Adjust to the actual field you want to search
        )

    return render(request, 'Administrator/publisher_management.html', {'publishers': publishers, 'search_query': query})

@login_required(login_url='/administrator/login')
def block_publisher(request, publisher_id):
    publisher = get_object_or_404(Publisher, id=publisher_id)
    if request.method == 'POST':
        publisher.is_active = False
        publisher.save()
        # Send email notification
        send_email_notification(publisher.email, 'Publisher Blocked', 'Publisher blocked successfully.')
        messages.success(request, 'Publisher blocked successfully.')
        return redirect('Administrator:publisher_management')
    return render(request, 'Administrator/block_publisher.html', {'publisher': publisher})

@login_required(login_url='/administrator/login')
def unblock_publisher(request, publisher_id):
    publisher = get_object_or_404(Publisher, id=publisher_id)
    if request.method == 'POST':
        publisher.is_active = True
        publisher.save()
        # Send email notification
        send_email_notification(publisher.email, 'Publisher Unblocked', 'Publisher unblocked successfully.')
        messages.success(request, 'Publisher unblocked successfully.')
        return redirect('Administrator:publisher_management')
    return render(request, 'Administrator/unblock_publisher.html', {'publisher': publisher})

@login_required(login_url='/administrator/login')
def delete_publisher(request, publisher_id):
    publisher = get_object_or_404(Publisher, id=publisher_id)
    if request.method == 'POST':
        # Delete related content
        apps = App.objects.filter(publisher=publisher)
        games = Game.objects.filter(publisher=publisher)
        ebooks = eBook.objects.filter(publisher=publisher)

        # Delete media files
        for app in apps:
            delete_media_files(app)
            app.delete()
        for game in games:
            delete_media_files(game)
            game.delete()
        for ebook in ebooks:
            delete_media_files(ebook)
            ebook.delete()

        # Send email notification
        send_email_notification(publisher.email, 'Publisher Deleted', f'The publisher {publisher.username} has been deleted.')
        
        # Delete the publisher
        publisher.delete()
        messages.success(request, f'Publisher {publisher.username} has been deleted successfully.')
        return redirect('Administrator:publisher_management')

    return render(request, 'Administrator/delete_publisher.html', {'publisher': publisher})

def delete_media_files(content):
    media_fields = ['logo', 'cover_image1', 'cover_image2', 'cover_image3', 'cover_image4', 'file_path']
    for field in media_fields:
        media_file = getattr(content, field, None)
        if media_file:
            file_path = os.path.join(settings.MEDIA_ROOT, media_file.name)
            if os.path.isfile(file_path):
                os.remove(file_path)

@login_required(login_url='/administrator/login')
def content_management(request):
    query = request.GET.get('q')
    contents = Content.objects.all()

    if query:
        contents = contents.filter(
            title__icontains=query
        )

    return render(request, 'Administrator/content_management.html', {'contents': contents, 'search_query': query})

@login_required(login_url='/administrator/login')
def block_content(request, content_id):
    content = get_object_or_404(Content, id=content_id)
    if request.method == 'POST':
        # Block content
        content.status = 'Blocked'
        content.save()
        # Send email notification
        send_email_notification(content.publisher.email, 'Content Blocked', f'The content "{content.title}" has been blocked.')
        messages.success(request, 'Content blocked successfully.')
        return redirect('Administrator:content_management')
    return render(request, 'Administrator/block_content.html', {'content': content})

@login_required(login_url='/administrator/login')
def unblock_content(request, content_id):
    content = get_object_or_404(Content, id=content_id)
    if request.method == 'POST':
        # Unblock content
        content.status = 'Active'
        content.save()
        # Send email notification
        send_email_notification(content.publisher.email, 'Content Unblocked', f'The content "{content.title}" has been unblocked.')
        messages.success(request, 'Content unblocked successfully.')
        return redirect('Administrator:content_management')
    return render(request, 'Administrator/unblock_content.html', {'content': content})

def delete_media_files(content):
    media_files = [
        content.logo,
        content.cover_image1,
        content.cover_image2,
        content.cover_image3,
        content.cover_image4,
    ]
    
    for media_file in media_files:
        if media_file and hasattr(media_file, 'path') and os.path.isfile(media_file.path):
            os.remove(media_file.path)
    
    # Handle file_path separately since it's a CharField
    if content.file_path:
        file_path = os.path.join(settings.MEDIA_ROOT, content.file_path)
        if os.path.isfile(file_path):
            os.remove(file_path)

@login_required(login_url='/administrator/login')
def delete_content(request, content_id):
    content = get_object_or_404(Content, id=content_id)
    if request.method == 'POST':
        # Delete associated media files
        delete_media_files(content)
        
        # Delete content
        content.delete()
        
        # Send email notification
        send_email_notification(content.publisher.email, 'Content Deleted', f'The content "{content.title}" has been deleted.')
        messages.success(request, 'Content deleted successfully.')
        return redirect('Administrator:content_management')
    
    return render(request, 'Administrator/delete_content.html', {'content': content})

@login_required(login_url='/administrator/login')
def admin_announcements(request):
    if request.method == 'POST':
        subject = request.POST.get('subject')
        message = request.POST.get('message')
        send_to_publishers = request.POST.get('send_to_publishers') == 'on'
        send_to_users = request.POST.get('send_to_users') == 'on'

        announcement = Announcement.objects.create(
            title=subject,  # Using 'title' field from the model
            content=message,  # Using 'content' field from the model
        )

        recipients = []
        if send_to_publishers:
            publishers_emails = [publisher.email for publisher in Publisher.objects.filter(is_active=True)]
            recipients.extend(publishers_emails)
        if send_to_users:
            users_emails = [user.email for user in User.objects.filter(is_active=True)]
            recipients.extend(users_emails)

        if recipients:
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                recipients,
                fail_silently=False,
            )

        messages.success(request, 'Announcement sent successfully.')
        return redirect('Administrator:admin_announcements')

    announcements = Announcement.objects.all().order_by('-created_at')

    return render(request, 'Administrator/admin_announcements.html', {'announcements': announcements})

def send_email_notification(to_email, subject, message):
    """Function to send email notifications."""
    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [to_email],
        fail_silently=False,
    )