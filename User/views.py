from django.shortcuts import render, get_object_or_404
from django.contrib.auth import authenticate, login as auth_login
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from .models import *
from Publisher.models import *
from django.contrib.auth.hashers import make_password
from django.contrib.auth import get_user_model
from .utils import generate_otp, send_otp_email
from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.hashers import check_password
import random
from django.conf import settings
from django.contrib import messages
from django.utils.crypto import get_random_string
from django.contrib.auth import update_session_auth_hash
from django.template.loader import render_to_string
from django.core.mail import EmailMessage
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import logout as auth_logout
from django.http import HttpResponse, Http404
import os

from Administrator.views import send_email_notification

@login_required(login_url='/user/login/')
def user_home(request):
    # Fetch content without filtering by status
    apps = list(App.objects.all())
    games = list(Game.objects.all())
    ebooks = list(eBook.objects.all())
    
    # Shuffle the lists for randomness
    random.shuffle(apps)
    random.shuffle(games)
    random.shuffle(ebooks)
    
    # Limit the number of items to show
    featured_apps = apps[:3]
    featured_games = games[:3]
    featured_ebooks = ebooks[:3]

    # Check purchase status for apps, games, and ebooks
    for app in featured_apps:
        app.purchased = Purchase.objects.filter(user=request.user, app_id=app.id).exists() if app.type == 'paid' else True
    
    for game in featured_games:
        game.purchased = Purchase.objects.filter(user=request.user, game_id=game.id).exists() if game.type == 'paid' else True
    
    for ebook in featured_ebooks:
        ebook.purchased = Purchase.objects.filter(user=request.user, ebook_id=ebook.id).exists() if ebook.type == 'paid' else True
    
    context = {
        'user': request.user,
        'featured_apps': featured_apps,
        'featured_games': featured_games,
        'featured_ebooks': featured_ebooks,
    }
    return render(request, 'User/home.html', context)

def login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            if user.is_active:
                auth_login(request, user)
                request.session['UserType'] = 'User'
                return redirect('User:user_home')  # Redirect to user home after login
            else:
                # Handle inactive account
                messages.error(request, 'Your account is currently inactive.')
                return render(request, 'User/login.html', {'error_message':'Your account is currently blocked.'})
        else:
            # Handle invalid login
            messages.error(request, 'Invalid username or password.')
            return render(request, 'User/login.html', {'error_message': 'Invalid username or password.'})
    else:
        return render(request, 'User/login.html')

def logout(request):
    auth_logout(request)
    return redirect('User:user_login')

def signup(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        hashed_password = make_password(password)  # Hash the password before saving
        
        # Create a new User object
        new_user = User(username=username, email=email, password=hashed_password)
        new_user.save()

        # Redirect to login page after successful signup
        return redirect('User:user_home')
    else:
        return render(request, 'User/signup.html')

def login_with_otp(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return render(request, 'User/login_with_otp.html', {'error_message': 'No user found with this email.'})
        
        otp = generate_otp()
        send_otp_email(email, otp, 'Login')
        request.session['login_email'] = email
        request.session['login_otp'] = otp
        return redirect('User:user_verify_login_otp')
    else:
        return render(request, 'User/login_with_otp.html')

def verify_login_otp(request):
    if request.method == 'POST':
        entered_otp = request.POST.get('otp')
        saved_otp = request.session.get('login_otp')
        
        if entered_otp == saved_otp:
            email = request.session.get('login_email')
            try:
                user = User.objects.get(email=email)
                
                # Clear OTP-related session data
                del request.session['login_otp']
                del request.session['login_email']
                
                # Manually log the user in by setting the backend attribute
                user.backend = 'django.contrib.auth.backends.ModelBackend'
                auth_login(request, user)
                
                return redirect('User:user_home')
            except User.DoesNotExist:
                return render(request, 'User/verify_login_otp.html', {'error_message': 'User not found.'})
        else:
            return render(request, 'User/verify_login_otp.html', {'error_message': 'Invalid OTP.'})
    else:
        return render(request, 'User/verify_login_otp.html')
        
def forgot_password(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return render(request, 'User/forgot_password.html', {'error_message': 'No user found with this email.'})
        
        otp = generate_otp()
        send_otp_email(email, otp, 'Password Reset')
        request.session['reset_email'] = email
        request.session['reset_otp'] = otp
        return redirect('User:user_verify_otp')
    else:
        return render(request, 'User/forgot_password.html')

def verify_otp(request):
    if request.method == 'POST':
        entered_otp = request.POST.get('otp')
        saved_otp = request.session.get('reset_otp')
        if entered_otp == saved_otp:
            return redirect('User:user_change_password')
        else:
            return render(request, 'User/verify_otp.html', {'error_message': 'Invalid OTP.'})
    else:
        return render(request, 'User/verify_otp.html')

def change_password(request):
    if request.method == 'POST':
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')
        if new_password == confirm_password:
            email = request.session.get('reset_email')
            user = User.objects.get(email=email)
            user.set_password(new_password)
            user.save()
            return redirect('User:user_login')
        else:
            return render(request, 'User/change_password.html', {'error_message': 'Passwords do not match.'})
    else:
        return render(request, 'User/change_password.html')

@login_required(login_url='/user/login/')
def browse_apps(request):
    apps = App.objects.filter(status='Active')  # Get all apps
    
    # Filter by search query
    query = request.GET.get('q')
    if query:
        keywords = query.split()
        filtered_apps = apps
        for keyword in keywords:
            filtered_apps = filtered_apps.filter(title__icontains=keyword)
        apps = filtered_apps
    
    # Filter by category
    category_id = request.GET.get('category')
    if category_id:
        apps = apps.filter(categories__id=category_id)
    
    # Apply sorting
    sort = request.GET.get('sort', 'title')  # Default sorting by title
    apps = apps.order_by(sort)
    
    categories = Category.objects.all()  # Fetch all categories

    #purchased apps
    purchased_apps = Purchase.objects.filter(user=request.user, app__isnull=False).values_list('app_id', flat=True)
    
    context = {
        'apps': apps,
        'categories': categories,
        'search_query': query,  
        'purchased_apps': purchased_apps,
    }
    return render(request, 'User/browse_apps.html', context)


@login_required(login_url='/user/login/')
def browse_games(request):
    games = Game.objects.filter(status='Active')  # Get all games
    
    # Filter by search query
    query = request.GET.get('q')
    if query:
        keywords = query.split()
        filtered_games = games
        for keyword in keywords:
            filtered_games = filtered_games.filter(title__icontains=keyword)
        games = filtered_games
    
    # Filter by category
    category_id = request.GET.get('category')
    if category_id:
        games = games.filter(categories__id=category_id)
    
    # Apply sorting
    sort = request.GET.get('sort', 'title')  # Default sorting by title
    games = games.order_by(sort)
    
    categories = Category.objects.all()  # Fetch all categories
    
    #purchased apps
    purchased_games = Purchase.objects.filter(user=request.user, game__isnull=False).values_list('game_id', flat=True)

    context = {
        'games': games,
        'categories': categories,
        'search_query': query,
        'purchased_games': purchased_games,
    }
    return render(request, 'User/browse_games.html', context)


@login_required(login_url='/user/login/')
def browse_ebooks(request):
    ebooks = eBook.objects.filter(status='Active')  # Get all eBooks
    
    # Filter by search query
    query = request.GET.get('q')
    if query:
        keywords = query.split()
        filtered_ebooks = ebooks
        for keyword in keywords:
            filtered_ebooks = filtered_ebooks.filter(title__icontains=keyword)
        ebooks = filtered_ebooks
    
    # Filter by category
    category_id = request.GET.get('category')
    if category_id:
        ebooks = ebooks.filter(categories__id=category_id)
    
    # Apply sorting
    sort = request.GET.get('sort', 'title')  # Default sorting by title
    ebooks = ebooks.order_by(sort)
    
    categories = Category.objects.all()  # Fetch all categories
    
    # Get purchased ebooks by the current user
    purchased_ebooks = Purchase.objects.filter(user=request.user, ebook__isnull=False).values_list('ebook_id', flat=True)
    
    context = {
        'ebooks': ebooks,
        'categories': categories,
        'search_query': query,  # Pass the search query to retain in the form input
        'purchased_ebooks': purchased_ebooks,
    }
    return render(request, 'User/browse_ebooks.html', context)

@login_required(login_url='/user/login/')
def content_detail(request, content_type, content_id):
    model_mapping = {
        'app': App,
        'game': Game,
        'ebook': eBook,
    }
    model = model_mapping.get(content_type)
    if not model:
        raise Http404("Content type does not exist")

    content = get_object_or_404(model, id=content_id)
    if content.status == 'Blocked':
        return render(request, 'User:user_home')

    # Check if the user has purchased the content
    if content_type == 'app':
        purchased = Purchase.objects.filter(user=request.user, app_id=content_id).exists()
    elif content_type == 'game':
        purchased = Purchase.objects.filter(user=request.user, game_id=content_id).exists()
    elif content_type == 'ebook':
        purchased = Purchase.objects.filter(user=request.user, ebook_id=content_id).exists()
    else:
        purchased = False

    # Fetch reviews related to the content
    reviews = Review.objects.filter(content_id=content_id)

    return render(request, 'User/content_detail.html', {'content': content, 'content_type': content_type, 'purchased': purchased, 'reviews': reviews})

@login_required(login_url='/user/login/')
def process_purchase(request, content_type, content_id):
    # Mapping of content type to model class
    model_mapping = {
        'app': App,
        'game': Game,
        'ebook': eBook,
    }

    # Retrieve the appropriate model class based on content_type
    model = model_mapping.get(content_type)
    if not model:
        raise Http404("Content type does not exist")

    # Retrieve the content object based on model and content_id
    content = get_object_or_404(model, id=content_id)
    user = request.user

    # Check if the user has already purchased this content
    if Purchase.objects.filter(user=user, **{f"{content_type}_id": content_id}).exists():
        messages.info(request, 'You have already purchased this content.')
    else:
        # Create a new purchase record for the specified content type
        purchase = Purchase(user=user)
        if content_type == 'app':
            purchase.app = content
        elif content_type == 'game':
            purchase.game = content
        elif content_type == 'ebook':
            purchase.ebook = content
        purchase.save()
        messages.success(request, 'Purchase successful! The content has been added to your library.')

    # Redirect to the content detail page based on content_type and content_id
    return redirect('User:content_detail', content_type=content_type, content_id=content.id)

@login_required(login_url='/user/login/')
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

    if content.status != 'Blocked':
        return redirect('User:user_home')

    # Construct the full file path
    file_path = os.path.join(settings.MEDIA_ROOT, content.file_path)

    if os.path.exists(file_path):
        with open(file_path, 'rb') as file:
            response = HttpResponse(file, content_type='application/octet-stream')
            response['Content-Disposition'] = 'attachment; filename=' + os.path.basename(file_path)
            return response
    else:
        raise Http404("File not found.")

@login_required(login_url='/user/login/')
def my_library(request):
    purchases = Purchase.objects.filter(user=request.user)
    content_list = []
    for purchase in purchases:
        if purchase.app:
            content_list.append({'type': 'app', 'content': purchase.app})
        elif purchase.game:
            content_list.append({'type': 'game', 'content': purchase.game})
        elif purchase.ebook:
            content_list.append({'type': 'ebook', 'content': purchase.ebook})

    context = {
        'content_list': content_list,
    }
    return render(request, 'User/my_library.html', context)

@login_required(login_url='/user/login/')
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
                otp_code = get_random_string(length=6, allowed_chars='1234567890')
                request.session['account_changes_otp'] = otp_code  # Store OTP in session
                
                # Send OTP via email
                send_otp_email(old_email, otp_code, 'Email Change')
                
                # Redirect to OTP verification page
                return redirect('User:verify_update_otp', action='email_change')
            
            elif new_password:
                # Change password without OTP verification
                user.set_password(new_password)
                user.save()
                
                # Update session authentication hash to prevent logging out
                update_session_auth_hash(request, user)
                
                messages.success(request, 'Password changed successfully.')
                return redirect('User:account_settings')
            else:
                # No changes made, display old data
                messages.info(request, 'No changes made.')
                return render(request, 'User/account_settings.html', {'user': user})

        elif action == 'deleteAccount':
            # Delete the user and all related data
            user.delete()
            messages.success(request, 'Account deleted successfully.')
            return redirect('User:login')

    return render(request, 'User/account_settings.html', {'user': request.user})

@login_required(login_url='/user/login/')
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
                return redirect('User:User:account_settings')
            # Add more actions if needed
            
        else:
            messages.error(request, 'Invalid OTP. Please try again.')

    return render(request, 'User/verify_otp.html', {'action': action})

@login_required(login_url='/user/login/')
def support(request):
    if request.method == 'POST':
        subject = request.POST.get('subject')
        message = request.POST.get('message')
        
        # Assuming you have a logged-in user
        user = request.user
        
        # Create a new support ticket
        SupportTicket.objects.create(user=user, subject=subject, message=message)
        
        messages.success(request, 'Ticket submitted successfully.')
        return redirect('User:User:support')

    # Fetch all user's tickets
    user_tickets = SupportTicket.objects.filter(user=request.user).order_by('-created_at')

    return render(request, 'User/support.html', {'user_tickets': user_tickets})

@login_required(login_url='/user/login')
def submit_review(request, content_id):
    content = get_object_or_404(Content, pk=content_id)
    
    if request.method == 'POST':
        rating = request.POST.get('rating')
        text = request.POST.get('text')
        
        # Ensure request.user is a User instance
        if isinstance(request.user, User):
            if rating and text:
                review = Review(user=request.user, content=content, rating=rating, text=text)
                review.save()
                messages.success(request, 'Review submitted successfully.')
                return redirect('User:content_detail', content_type=content.content_type, content_id=content.id)
            else:
                messages.error(request, 'Please provide both rating and review text.')
        else:
            messages.error(request, 'You must be logged in as a User to submit a review.')

    reviews = Review.objects.filter(content=content).order_by('-created_at')
    return render(request, 'User/content_review.html', {'content': content, 'reviews': reviews})