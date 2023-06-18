from django.conf import settings
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("User must have an email address.")

        user = self.model(email=self.normalize_email(email), **extra_fields)
        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_superuser(self, email, password=None, **extra_fields):
        return self.create_user(email, password, is_superuser=True, is_staff=True, **extra_fields)


class User(PermissionsMixin, AbstractBaseUser):
    email = models.EmailField(max_length=255, unique=True)
    name = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    USERNAME_FIELD = "email"

    objects = UserManager()

    def __str__(self):
        return self.name


class Recipe(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="recipes"
    )
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    time_minutes = models.IntegerField()
    price = models.DecimalField(max_digits=5, decimal_places=2)
    link = models.CharField(max_length=255, blank=True)
    tags = models.ManyToManyField("Tag", related_name="recipes")
    ingredients = models.ManyToManyField("Ingredient", related_name="recipes")

    def __str__(self):
        return self.title


class Tag(models.Model):
    """Model for filtering recipes."""

    name = models.CharField(max_length=100)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="tags")

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    """Ingredient for recipes."""

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="ingredients")
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name
