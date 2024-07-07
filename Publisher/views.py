from django.shortcuts import render, get_object_or_404
from django.contrib.auth import authenticate, login as auth_login
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from .models import *
from User.models import *
from django.contrib.auth.hashers import make_password
from .utils import generate_otp, send_otp_email
from django.contrib.auth.backends import ModelBackend
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth import logout as auth_logout
# from .forms import ContentForm
from django.core.files.storage import FileSystemStorage
from django.conf import settings
from django.db.models import Sum
from django.contrib.auth import logout as auth_logout
from django.http import HttpResponse, Http404
import os
from django.conf import settings
from Administrator.views import send_email_notification

@login_required(login_url='/publisher/login/')
def publisher_home(request):
    # Get total content count
    total_apps = App.objects.filter(publisher=request.user).count()
    total_games = Game.objects.filter(publisher=request.user).count()
    total_ebooks = eBook.objects.filter(publisher=request.user).count()
    total_content = total_apps + total_games + total_ebooks

    # Get total sales count (assuming Purchase model is properly set up)
    total_sales = Purchase.objects.filter(app__publisher=request.user).count()  # Adjust for Game and eBook accordingly

    # Get total reviews count for the publisher's content
    total_reviews = Review.objects.filter(content__publisher=request.user).count()

    # Get recent content (assuming you have a way to fetch recent content)
    recent_content = Content.objects.filter(publisher=request.user).order_by('-created_at')[:5]

    context = {
        'total_content': total_content,
        'total_sales': total_sales,
        'total_reviews': total_reviews,
        'recent_content': recent_content,
    }

    return render(request, 'Publisher/home.html', context)

@login_required(login_url='/publisher/login/')
def publisher_reviews(request):
    # Get reviews for the publisher's content
    publisher_reviews = Review.objects.filter(content__publisher=request.user)

    context = {
        'publisher_reviews': publisher_reviews,
    }

    return render(request, 'Publisher/publisher_reviews.html', context)

from django.contrib.auth import authenticate, login as auth_login
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.models import User

def login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            if user.is_active:
                auth_login(request, user)
                request.session['UserType'] = 'Publisher'
                return redirect('Publisher:publisher_home')  # Redirect to publisher dashboard after login
            else:
                # Handle inactive account
                messages.error(request, 'Your account is currently inactive.')
                return render(request, 'Publisher/login.html',{'error_message':'Your account is currently blocked.'})
        else:
            # Handle invalid login
            messages.error(request, 'Invalid username or password.')
            return render(request, 'Publisher/login.html', {'error_message':'Invalid username or password.'})
    else:
        return render(request, 'Publisher/login.html')

def logout(request):
    auth_logout(request)
    return redirect('Publisher:publisher_login')

def signup(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        hashed_password = make_password(password)  # Hash the password before saving
        
        # Create a new Publisher object
        new_publisher = Publisher(username=username, email=email, password=hashed_password)
        new_publisher.save()

        # Redirect to login page after successful signup
        return redirect('Publisher:publisher_home')
    else:
        return render(request, 'Publisher/signup.html')

def login_with_otp(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        try:
            publisher = Publisher.objects.get(email=email)
        except Publisher.DoesNotExist:
            return render(request, 'Publisher/login_with_otp.html', {'error_message': 'No publisher found with this email.'})
        
        otp = generate_otp()
        send_otp_email(email, otp, 'Login')
        request.session['login_email'] = email
        request.session['login_otp'] = otp
        return redirect('Publisher:publisher_verify_login_otp')
    else:
        return render(request, 'Publisher/login_with_otp.html')

def verify_login_otp(request):
    if request.method == 'POST':
        entered_otp = request.POST.get('otp')
        saved_otp = request.session.get('login_otp')
        if entered_otp == saved_otp:
            email = request.session.get('login_email')
            publisher = Publisher.objects.get(email=email)
            # Explicitly set the authentication backend
            publisher.backend = f"{publisher._meta.app_label}.{ModelBackend.__name__}"
            auth_login(request, publisher)
            return redirect('Publisher:publisher_home')
        else:
            return render(request, 'Publisher/verify_login_otp.html', {'error_message': 'Invalid OTP.'})
    else:
        return render(request, 'Publisher/verify_login_otp.html')

def forgot_password(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        try:
            user = Publisher.objects.get(email=email)
        except Publisher.DoesNotExist:
            return render(request, 'Publisher/forgot_password.html', {'error_message': 'No publisher found with this email.'})
        
        otp = generate_otp()
        send_otp_email(email, otp, 'Password Reset')
        request.session['reset_email'] = email
        request.session['reset_otp'] = otp
        return redirect('Publisher:verify_otp')
    else:
        return render(request, 'Publisher/forgot_password.html')

def verify_otp(request):
    if request.method == 'POST':
        entered_otp = request.POST.get('otp')
        saved_otp = request.session.get('reset_otp')
        if entered_otp == saved_otp:
            return redirect('Publisher:publisher_change_password')
        else:
            return render(request, 'Publisher/verify_otp.html', {'error_message': 'Invalid OTP.'})
    else:
        return render(request, 'Publisher/verify_otp.html')

def change_password(request):
    if request.method == 'POST':
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')
        if new_password == confirm_password:
            email = request.session.get('reset_email')
            user = Publisher.objects.get(email=email)
            user.set_password(new_password)
            user.save()
            return redirect('Publisher:publisher_login')
        else:
            return render(request, 'Publisher/change_password.html', {'error_message': 'Passwords do not match.'})
    else:
        return render(request, 'Publisher/change_password.html')

@login_required(login_url='/publisher/login/')
def account_settings(request):
    if request.method == 'POST':
        action = request.POST.get('action')
        user = request.user

        if action == 'saveChanges':
            new_email = request.POST.get('new_email')
            new_password = request.POST.get('new_password')
            
            if new_email:
                old_email = user.email
                request.session['new_email'] = new_email  # Store new email in session
                
                # Send OTP to the old email for verification
                otp_code = generate_otp()
                request.session['account_changes_otp'] = otp_code  # Store OTP in session
                
                # Send OTP via email
                send_otp_email(old_email, otp_code, 'Email Change')
                
                # Redirect to OTP verification page
                return redirect('Publisher:verify_update_otp', action='email_change')
            
            elif new_password:
                # Change password without OTP verification
                user.set_password(new_password)
                user.save()
                
                # Update session authentication hash to prevent logging out
                update_session_auth_hash(request, user)
                
                messages.success(request, 'Password changed successfully.')
                return redirect('Publisher:account_settings')
            else:
                # No changes made, display old data
                messages.info(request, 'No changes made.')
                return render(request, 'Publisher/account_settings.html', {'user': user})

        elif action == 'deleteAccount':
            # Delete all related content (apps, games, ebooks)
            apps = App.objects.filter(publisher=user)
            games = Game.objects.filter(publisher=user)
            ebooks = eBook.objects.filter(publisher=user)
            
            # Delete media files
            for content in list(apps) + list(games) + list(ebooks):
                media_files = [
                    content.logo,
                    content.cover_image1,
                    content.cover_image2,
                    content.cover_image3,
                    content.cover_image4,
                    content.file_path,
                ]
                for media_file in media_files:
                    if media_file and default_storage.exists(media_file.path):
                        default_storage.delete(media_file.path)
                content.delete()

            # Delete the user (publisher) and send notification
            send_email_notification(user.email, 'Account Deleted', 'Your publisher account has been deleted successfully.')
            user.delete()
            messages.success(request, 'Account deleted successfully.')
            return redirect('Publisher:publisher_login')

    return render(request, 'Publisher/account_settings.html', {'user': request.user})

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
                return redirect('Publisher:account_settings')
            # Add more actions if needed
            
        else:
            messages.error(request, 'Invalid OTP. Please try again.')

    return render(request, 'Publisher/verify_update_otp.html', {'action': action})

@login_required(login_url='/publisher/login/')
def publisher_dashboard(request):
    total_content = Content.objects.filter(publisher=request.user).count()
    total_sales = Order.objects.filter(content__publisher=request.user).count()
    total_reviews = Review.objects.filter(content__publisher=request.user).count()
    recent_content = Content.objects.filter(publisher=request.user).order_by('-id')[:5]

    context = {
        'total_content': total_content,
        'total_sales': total_sales,
        'total_reviews': total_reviews,
        'recent_content': recent_content,
    }
    
    return render(request, 'Publisher/publisher_dashboard.html', context)

@login_required(login_url='/publisher/login/')
def publisher_my_content(request):
    content_list = Content.objects.filter(publisher=request.user)
    
    context = {
        'content_list': content_list,
    }
    
    return render(request, 'Publisher/publisher_my_content.html', context)

@login_required(login_url='/publisher/login/')
def publisher_edit_content(request, content_id):
    content = get_object_or_404(Content, id=content_id)
    
    if request.method == 'POST':
        # Update content fields
        content.title = request.POST.get('title')
        content.description = request.POST.get('description')
        
        # Handle logo, cover images, and APK file
        if request.FILES.get('logo'):
            content.logo = request.FILES['logo']
        if request.FILES.get('cover_image1'):
            content.cover_image1 = request.FILES['cover_image1']
        if request.FILES.get('cover_image2'):
            content.cover_image2 = request.FILES['cover_image2']
        if request.FILES.get('cover_image3'):
            content.cover_image3 = request.FILES['cover_image3']
        if request.FILES.get('cover_image4'):
            content.cover_image4 = request.FILES['cover_image4']
        if request.FILES.get('apk_file'):
            content.apk_file = request.FILES['apk_file']
            content.apk_version = request.POST.get('apk_version')  # Assuming 'apk_version' is the name of the input field
        
        # Save the updated content
        content.save()
        
        # Redirect to the content list view
        return redirect('Publisher:publisher_my_content')  # Ensure 'publisher' namespace is correct
       
    context = {
        'content': content,
    }
    
    return render(request, 'Publisher/publisher_edit_content.html', context)

@login_required(login_url='/publisher/login')
def content_download(request, content_type, content_id):
    # Map content_type to corresponding model
    model_mapping = {
        'app': App,
        'game': Game,
        'ebook': eBook,
    }
    
    model = model_mapping.get(content_type)
    if not model:
        raise Http404("Content type does not exist")

    # Fetch the content object
    content = get_object_or_404(model, id=content_id)

    # Construct the full file path
    file_path = os.path.join(settings.MEDIA_ROOT, content.file_path)

    if os.path.exists(file_path):
        with open(file_path, 'rb') as file:
            response = HttpResponse(file, content_type='application/octet-stream')
            response['Content-Disposition'] = 'attachment; filename=' + os.path.basename(file_path)
            return response
    else:
        raise Http404("File not found.")


@login_required(login_url='/publisher/login/')
def publisher_delete_content(request, content_id):
    content = get_object_or_404(Content, id=content_id)
    
    if request.method == 'POST':
        content.delete()
        return redirect('Publisher:publisher_my_content')
    
    context = {
        'content': content,
    }
    
    return render(request, 'Publisher/publisher_delete_content.html', context)

@login_required(login_url='/publisher/login/')
def publisher_upload(request):
    if request.method == 'POST':
        title = request.POST['title']
        description = request.POST['description']
        logo = request.FILES['logo']
        cover_image1 = request.FILES['cover_image1']
        cover_image2 = request.FILES['cover_image2']
        cover_image3 = request.FILES['cover_image3']
        cover_image4 = request.FILES['cover_image4']
        content_type = request.POST['content_type']
        content_status = request.POST['type']
        file_path = request.FILES['file']
        apk_version = request.POST.get('apk_version')
        
        # Save the file and get the path
        fs = FileSystemStorage()
        file_name = fs.save(file_path.name, file_path)
        file_url = fs.url(file_name)
        
        # Handle price
        price = None
        if content_status == 'paid':
            price = request.POST['price']
        
        # Remove '/media/' from file_path for storage
        if file_url.startswith('/media/'):
            file_path = file_url[7:]  # Remove '/media/' part
        
        # Create content object
        content = None
        if content_type == 'app':
            content = App(
                title=title,
                description=description,
                publisher=request.user,
                logo=logo,
                cover_image1=cover_image1,
                cover_image2=cover_image2,
                cover_image3=cover_image3,
                cover_image4=cover_image4,
                type=content_status,
                content_type=content_type,
                file_path=file_path,
                apk_version=apk_version,
                price=price
            )
        elif content_type == 'game':
            content = Game(
                title=title,
                description=description,
                publisher=request.user,
                logo=logo,
                cover_image1=cover_image1,
                cover_image2=cover_image2,
                cover_image3=cover_image3,
                cover_image4=cover_image4,
                type=content_status,
                content_type=content_type,
                file_path=file_path,
                apk_version=apk_version,
                price=price
            )
        elif content_type == 'ebook':
            content = eBook(
                title=title,
                description=description,
                publisher=request.user,
                logo=logo,
                cover_image1=cover_image1,
                cover_image2=cover_image2,
                cover_image3=cover_image3,
                cover_image4=cover_image4,
                type=content_status,
                content_type=content_type,
                file_path=file_path,
                apk_version=apk_version,
                price=price
            )
        
        content.save()
        return redirect('Publisher:publisher_my_content')  # Redirect to publisher's content page

    return render(request, 'Publisher/publisher_upload.html')

@login_required(login_url='/publisher/login/')
def publisher_sales_reports(request):
    # Get all apps, games, and ebooks published by the current publisher
    apps = App.objects.filter(publisher=request.user)
    games = Game.objects.filter(publisher=request.user)
    ebooks = eBook.objects.filter(publisher=request.user)

    # Calculate total sales for each content type
    app_sales = Purchase.objects.filter(app__in=apps).aggregate(total_sales=Sum('app__price'))['total_sales'] or 0
    game_sales = Purchase.objects.filter(game__in=games).aggregate(total_sales=Sum('game__price'))['total_sales'] or 0
    ebook_sales = Purchase.objects.filter(ebook__in=ebooks).aggregate(total_sales=Sum('ebook__price'))['total_sales'] or 0

    context = {
        'app_sales': app_sales,
        'game_sales': game_sales,
        'ebook_sales': ebook_sales,
    }

    return render(request, 'Publisher/sales_reports.html', context)