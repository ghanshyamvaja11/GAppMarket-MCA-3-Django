from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.contrib.auth import get_user_model
from django.conf import settings

class PublisherManager(BaseUserManager):
    def create_user(self, username, email, password=None):
        if not email:
            raise ValueError('Publishers must have an email address')
        
        user = self.model(
            username=username,
            email=self.normalize_email(email),
        )
        
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email, password):
        user = self.create_user(
            username=username,
            email=email,
            password=password,
        )
        user.is_admin = True
        user.save(using=self._db)
        return user

class Publisher(AbstractBaseUser):
    username = models.CharField(max_length=100, unique=True)
    email = models.EmailField(verbose_name='email address', max_length=255, unique=True)
    date_joined = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)

    objects = PublisherManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return self.email

    def has_perm(self, perm, obj=None):
        return True

    def has_module_perms(self, app_label):
        return True

    @property
    def is_staff(self):
        return self.is_admin

class Content(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    publisher = models.ForeignKey(Publisher, on_delete=models.CASCADE)
    logo = models.ImageField(upload_to='content/logos/')
    cover_image1 = models.ImageField(upload_to='content/covers/')
    cover_image2 = models.ImageField(upload_to='content/covers/')
    cover_image3 = models.ImageField(upload_to='content/covers/')
    cover_image4 = models.ImageField(upload_to='content/covers/')
    type = models.CharField(max_length=4, choices=[('free', 'Free'), ('paid', 'Paid')], default='free')
    content_type = models.CharField(max_length=5, default='app')
    status = models.CharField(max_length=20, default='Active')
    file_path = models.CharField(max_length=150, default=None)
    apk_version = models.CharField(max_length=20, default=None)
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True) ,
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Content'
        verbose_name_plural = 'Contents'

    def __str__(self):
        return self.title

# Game Model
class Game(Content):
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

# App Model
class App(Content):
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

# eBook Model
class eBook(Content):
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

# Category Model
class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField()

    def __str__(self):
        return self.name

# Content Category Model
class ContentCategory(models.Model):
    content = models.ForeignKey(Content, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)

    class Meta:
        unique_together = ['content', 'category']

    def __str__(self):
        return f"{self.content.title} - {self.category.name}"