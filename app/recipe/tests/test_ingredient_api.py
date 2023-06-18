"""
    Tests for ingredients api.
"""
from core.models import Ingredient
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from recipe.serializers import IngredientSerializer
from rest_framework import status
from rest_framework.test import APIClient

User = get_user_model()

INGREDIENTS_URL = reverse("recipe:ingredient-list")


def create_user(email="user@example.com", password="test123"):
    """Create a test user."""
    return User.objects.create_user(email=email, password=password)


class PublicIngredientApiTests(TestCase):
    """Test unauthenticated API requests."""

    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        """Test auth is required for retrieving ingredients."""
        res = self.client.get(INGREDIENTS_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateIngredientApiTests(TestCase):
    """Test authenticated API reqeusts."""

    def setUp(self):
        self.user = create_user()
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_ingredients_list(self):
        """Test listing all ingredients."""
        Ingredient.objects.create(user=self.user, name="Ing 1")
        Ingredient.objects.create(user=self.user, name="Ing 2")

        res = self.client.get(INGREDIENTS_URL)

        ingredients = Ingredient.objects.filter(user=self.user).order_by("-name")

        serializer = IngredientSerializer(ingredients, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)
