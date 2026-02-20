import uuid
from django.db import models
from django.db.models import OneToOneField
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager


class UserManager(BaseUserManager):
    # For create user
    def create_user(self, first_name, last_name, email, password, phone_number=None, username=None):
        if not email:
            raise ValueError("Email field is required")
        if not password:
            raise ValueError("Password field is required")

        user = self.model(
            email=self.normalize_email(email),
            first_name=first_name,
            last_name=last_name,
            username=username,
            phone_number=phone_number
        )
        user.set_password(password)
        user.save()
        return user

    # For create superuser
    def create_superuser(self, first_name, last_name, email, password, username=None):
        user = self.create_user(
            first_name=first_name,
            last_name=last_name,
            username=username,
            email=self.normalize_email(email),
            password=password
        )
        user.is_admin = True
        user.is_active = True
        user.is_staff = True
        user.is_superadmin = True
        user.is_superuser = True
        user.is_deleted = False
        user.save()
        return user


# This model is for Handling Users. This model replaced django's default auth.user model Changed username field to
# email for user login action.
class User(AbstractBaseUser, PermissionsMixin):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    first_name = models.CharField(max_length=50, blank=True, null=True)
    last_name = models.CharField(max_length=50, blank=True, null=True)
    username = models.CharField(max_length=50, unique=True, blank=True, null=True)
    email = models.EmailField(max_length=100, unique=True)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    is_online = models.BooleanField(default=False)
    last_seen = models.DateTimeField(auto_now_add=True)

    # required fields
    date_joined = models.DateTimeField(auto_now_add=True)
    last_login = models.DateTimeField(auto_now_add=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_admin = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_superadmin = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False)

    # Add a related_name argument to avoid clash with auth.User.groups
    groups = models.ManyToManyField(
        'auth.Group',
        verbose_name=_('groups'),
        blank=True,
        related_name='custom_user_set',  # You can choose any meaningful name here
        related_query_name='user',
    )

    # Add a related_name argument to avoid clash with auth.User.user_permissions
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        verbose_name=_('user permissions'),
        blank=True,
        related_name='custom_user_set',  # You can choose any meaningful name here
        related_query_name='user',
    )

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['password', 'first_name', 'last_name', 'username']

    class Meta:
        db_table = 'accounts_user'
        verbose_name = _('user')
        verbose_name_plural = _('users')
        ordering = ('-date_joined', 'username')

    def __str__(self):
        return self.email

    def has_perm(self, perm, obj=None):
        """
        Return True if the user has the specified permission.
        Superusers have all permissions.
        """
        # Superusers have all permissions
        if self.is_superadmin:
            return True

        # Check specific permissions for staff
        if self.is_staff:
            return super().has_perm(perm, obj)

        # Other users: rely on Django's permission system
        return super().has_perm(perm, obj)

    def has_module_perms(self, app_label):
        """
        Return True if the user has any permissions in the given app.
        Superusers have all permissions.
        """
        # Superusers have all module permissions
        if self.is_superadmin:
            return True

        # Check specific module permissions for staff
        if self.is_staff:
            return super().has_module_perms(app_label)

        # Other users: rely on Django's permission system
        return super().has_module_perms(app_label)

    # def has_perm(self, perm, obj=None):
    #     # return self.is_admin
    #     return True
    #
    # def has_module_perms(self, app_label):
    #     return True
