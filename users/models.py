from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.utils.translation import ugettext_lazy as _


class UserManager(BaseUserManager):
    """Define a model manager for User model with no username field."""

    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        """Create and save a User with the given email and password."""
        if not email:
            raise ValueError('The given email must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        """Create and save a regular User with the given email and password."""
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        """Create and save a SuperUser with the given email and password."""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(email, password, **extra_fields)


class User(AbstractUser):
    """User model."""

    username = None
    email = models.EmailField(_('email address'), unique=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = UserManager()


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    my_email = models.CharField(max_length=256, default="", blank=True, null=True)
    my_name = models.CharField(max_length=256)
    country = models.CharField(max_length=256, null=True, blank=True)
    address = models.CharField(max_length=256, null=True, blank=True)
    first_name = models.CharField(max_length=256)
    last_name = models.CharField(max_length=256)
    user_mobile_number = models.IntegerField(default=0, null=True, blank=True)


class Records(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='RecordUser')
    item_name = models.CharField(max_length=50, blank=True, null=True)
    item_category = models.CharField(max_length=50, blank=True, null=True)


class Company(models.Model):
    ROLE_CHOICES = (
        ('ACTIVE', 'active'),
        ('INACTIVE', 'inactive'),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='company_user')
    user_list = models.ManyToManyField(User, null=True, blank=True)
    company_name = models.CharField(max_length=256)
    country = models.CharField(max_length=256, null=True, blank=True)
    address = models.CharField(max_length=256, null=True, blank=True)
    company_status = models.CharField(max_length=256, choices=ROLE_CHOICES, null=True, blank=True)
    number_of_employees = models.IntegerField(null=True, blank=True)


class Products(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='product_company')
    product_name = models.CharField(max_length=256)
    price = models.IntegerField()
    description = models.CharField(max_length=256, null=True, blank=True)


class RoleModel(models.Model):
    ROLE_CHOICES = (
        ('ADMIN', 'admin'),
        ('DIRECTOR', 'director'),
        ('EDITOR', 'editor'),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='role_profile')
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='role_company')
    identity = models.CharField(max_length=256, choices=ROLE_CHOICES)
