import pyotp
from django.db import models
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser
from django.utils.timezone import now
from django.conf import settings
import uuid
from points.models import ClassMaster

def generate_totp_secret():
    return pyotp.random_base32()


class UserManager(BaseUserManager):
    def create_user(self, username, email, password=None, name="", created_via_admin=False):
        if not email:
            raise ValueError('Users must have an email address')
        user = self.model(
            username=username,
            email=self.normalize_email(email),
            name=name,
            created_via_admin=created_via_admin,
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email, password=None):
        user = self.create_user(username, email, password=password, created_via_admin=True)
        user.is_admin = True
        user.save(using=self._db)
        return user


class User(AbstractBaseUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    username = models.CharField(max_length=50, unique=True)
    email = models.EmailField(max_length=255, unique=True)
    name = models.CharField(default='', blank=True, max_length=50)
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)
    created_via_admin = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=now, null=True, blank=True)

    objects = UserManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']

    def __str__(self):
        return self.username

    @property
    def is_staff(self):
        return self.is_admin

    def has_perm(self, perm, obj=None):
        return True

    def has_module_perms(self, app_label):
        return True

class UserProfile(models.Model):
    ROLE_CHOICES = (
        ('student', 'Student'),
        ('teacher', 'Teacher'),
        ('admin', 'Admin'),
    )

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="profile")
    image = models.ImageField(upload_to="profile/", default="profile/default.webp", blank=True)
    totp_secret = models.CharField(max_length=32, default=generate_totp_secret)
    is_totp_verified = models.BooleanField(default=False)

    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='student')
    comment = models.CharField(max_length=255, blank=True, default="")
    is_active_student = models.BooleanField(default=True)  
    class_ref = models.ForeignKey(ClassMaster, null=True, blank=True, on_delete=models.SET_NULL)

    def __str__(self):
        return self.user.username
    

class DeletedUserLog(models.Model):
    user_id = models.UUIDField()
    username = models.CharField(max_length=50)
    email = models.EmailField()
    name = models.CharField(max_length=50, blank=True, default="")
    deleted_at = models.DateTimeField(auto_now_add=True)
    deleted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="deleted_accounts"
    )

    def __str__(self):
        return f"{self.username} deleted at {self.deleted_at}"
