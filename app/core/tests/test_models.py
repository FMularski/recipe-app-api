from decimal import Decimal

from core import models
from django.contrib.auth import get_user_model
from django.test import TestCase


def create_user(email="user@example.com", password="testpass123"):
    """Create a new user."""
    return get_user_model().objects.create_user(email=email, password=password)


class ModelTests(TestCase):
    def test_create_user_with_email_successful(self):
        email = "test@example.com"
        password = "testpass123"
        user = get_user_model().objects.create_user(email=email, password=password)

        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))

    def test_new_user_email_normalized(self):
        sample_emails = [
            ["test1@EXAMPLE.com", "test1@example.com"],
            ["Test2@Example.com", "Test2@example.com"],
            ["TEST3@EXAMPLE.COM", "TEST3@example.com"],
            ["test4@example.COM", "test4@example.com"],
        ]

        for email, expected in sample_emails:
            user = get_user_model().objects.create_user(email, "sample123")
            self.assertEqual(user.email, expected)

    def test_new_user_without_email_raises_error(self):
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user("", "sample123")

    def test_create_superuser(self):
        user = get_user_model().objects.create_superuser("test@example.com", "test123")

        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)

    def test_create_recipe(self):
        user = get_user_model().objects.create_user("test@example.com", "sample123")

        recipe = models.Recipe.objects.create(
            user=user,
            title="Test recipe",
            time_minutes=5,
            price=Decimal("5.50"),
            description="Test desc",
        )

        self.assertEqual(str(recipe), recipe.title)

    def test_create_tag(self):
        """Test creating a tag i successful."""
        user = create_user()
        tag = models.Tag.objects.create(user=user, name="Tag 1")

        self.assertEqual(tag.name, str(tag))

    def test_create_ingredient(self):
        """Test creating an ingredient."""
        user = create_user()
        ingredient = models.Ingredient.objects.create(user=user, name="Ingredient 1")

        self.assertEqual(str(ingredient), ingredient.name)
