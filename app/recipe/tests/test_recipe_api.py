"""
    Tests for recipe api.
"""
from decimal import Decimal

from core.models import Recipe, Tag
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from recipe.serializers import RecipeDetailSerializer, RecipeSerializer
from rest_framework import status
from rest_framework.test import APIClient

RECIPES_URL = reverse("recipe:recipe-list")


def detail_url(recipe_id):
    """Create and return a recipe detail url."""
    return reverse("recipe:recipe-detail", args=(recipe_id,))


def create_recipe(user, **params):
    """Create and return a sample recipe."""
    defaults = {
        "title": "Test recipe",
        "time_minutes": 25,
        "price": Decimal("11.25"),
        "description": "Test desc",
        "link": "http://example.com/recipe.pdf",
    }
    defaults.update(params)
    recipe = Recipe.objects.create(user=user, **defaults)

    return recipe


def create_user(**params):
    """Create and return a new user."""
    return get_user_model().objects.create_user(**params)


class PublicRecipeApiTests(TestCase):
    """Test unauthenticated API requests."""

    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        """Test auth is required to call api."""
        response = self.client.get(RECIPES_URL)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateRecipeApiTests(TestCase):
    """Test authenticated API requests."""

    def setUp(self):
        self.client = APIClient()
        self.user = create_user(email="test@example.com", password="testpass123", name="Test Name")
        self.client.force_authenticate(self.user)

    def test_get_recipes_empty(self):
        """Test get empty recipes list."""
        response = self.client.get(RECIPES_URL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_recipes(self):
        """Test get recipes list."""
        create_recipe(user=self.user)
        create_recipe(user=self.user)
        create_recipe(user=self.user)

        response = self.client.get(RECIPES_URL)

        recipes = Recipe.objects.all().order_by("-id")
        serializer = RecipeSerializer(recipes, many=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_recipe_list_limited_to_user(self):
        """Test get recipes assigned to the user."""
        other_user = create_user(email="other@example.com", password="testpass123")

        create_recipe(user=self.user)
        create_recipe(user=other_user)

        response = self.client.get(RECIPES_URL)

        recipes = Recipe.objects.filter(user=self.user)
        serializer = RecipeSerializer(recipes, many=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_recipe_detail(self):
        recipe = create_recipe(user=self.user)
        url = detail_url(recipe.pk)

        response = self.client.get(url)

        serializer = RecipeDetailSerializer(recipe)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_create_recipe(self):
        payload = {
            "title": "Sample recipe",
            "time_minutes": 30,
            "price": Decimal("5.99"),
        }
        response = self.client.post(RECIPES_URL, payload)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        recipe = Recipe.objects.get(pk=response.data["id"])
        for k, v in payload.items():
            self.assertEqual(getattr(recipe, k), v)
        self.assertEqual(recipe.user, self.user)

    def test_partial_update(self):
        """Test partial update of a recipe."""
        original_link = "https://example.com/recipe.pdf"
        recipe = create_recipe(
            user=self.user,
            title="Sample title",
            link=original_link,
        )

        payload = {"title": "New title"}
        url = detail_url(recipe.pk)

        response = self.client.patch(url, payload)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        recipe.refresh_from_db()
        self.assertEqual(recipe.title, payload["title"])
        self.assertEqual(recipe.link, original_link)
        self.assertEqual(recipe.user, self.user)

    def test_full_update(self):
        """Test full update of a recipe."""
        recipe = create_recipe(
            user=self.user,
            title="Sample title",
            link="https://example.com/recipe.pdf",
            description="Sample description",
        )

        payload = {
            "title": "New title",
            "link": "https://example.com/new.pdf",
            "description": "New description",
            "time_minutes": 10,
            "price": Decimal("2.50"),
        }

        url = detail_url(recipe.pk)

        response = self.client.put(url, payload)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        recipe.refresh_from_db()
        for k, v in payload.items():
            self.assertEqual(getattr(recipe, k), v)
        self.assertEqual(recipe.user, self.user)

    def test_update_user_returns_error(self):
        """Test changing the recipe user results in an error."""
        new_user = create_user(email="other@example.com", password="test123")
        recipe = create_recipe(user=self.user)

        payload = {"user": new_user.pk}

        url = detail_url(recipe.pk)

        self.client.patch(url, payload)

        recipe.refresh_from_db()

        self.assertEqual(recipe.user, self.user)

    def test_delete_recipe(self):
        """Test deleting a recipe."""
        recipe = create_recipe(user=self.user)
        url = detail_url(recipe.pk)

        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Recipe.objects.filter(pk=recipe.pk).exists())

    def test_recipe_other_users_recipe_error(self):
        """Test trying to delete another user's recipe gives error."""
        new_user = create_user(email="test2@example.com", password="test123")
        recipe = create_recipe(user=new_user)

        url = detail_url(recipe.pk)
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertTrue(Recipe.objects.filter(pk=recipe.pk).exists())

    def test_create_recipe_with_new_tags(self):
        """Test creating a recipe with some new tags."""
        payload = {
            "title": "Title 1",
            "time_minutes": 30,
            "price": Decimal("3.50"),
            "tags": [{"name": "Tag 1"}, {"name": "Tag 2"}],
        }

        response = self.client.post(RECIPES_URL, payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        recipes = Recipe.objects.filter(user=self.user)
        self.assertEqual(recipes.count(), 1)
        recipe = recipes[0]
        self.assertEqual(recipe.tags.count(), 2)
        for tag in payload["tags"]:
            exists = recipe.tags.filter(name=tag["name"], user=self.user)
            self.assertTrue(exists)

    def test_create_recipe_with_existing_tags(self):
        """Test creating a recipe with some new tags."""

        tag1 = Tag.objects.create(user=self.user, name="Tag 1")
        tag2 = Tag.objects.create(user=self.user, name="Tag 2")

        payload = {
            "title": "Title 1",
            "time_minutes": 30,
            "price": Decimal("3.50"),
            "tags": [{"name": "Tag 1"}, {"name": "Tag 2"}],
        }

        response = self.client.post(RECIPES_URL, payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        recipes = Recipe.objects.filter(user=self.user)
        self.assertEqual(recipes.count(), 1)
        recipe = recipes[0]
        self.assertEqual(recipe.tags.count(), 2)
        self.assertIn(tag1, recipe.tags.all())
        self.assertIn(tag2, recipe.tags.all())

        for tag in payload["tags"]:
            exists = recipe.tags.filter(name=tag["name"], user=self.user)
            self.assertTrue(exists)

    def test_update_recipe_tags(self):
        """Test updating tags of a recipe."""
        tag1 = Tag.objects.create(user=self.user, name="Tag 1")
        Tag.objects.create(user=self.user, name="Tag 2")

        recipe = create_recipe(user=self.user)
        recipe.tags.add(tag1)

        payload = {"tags": [{"name": "Tag 2"}, {"name": "Tag 3"}]}

        url = detail_url(recipe.pk)
        response = self.client.patch(url, payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(recipe.tags.all()), 2)
        self.assertEqual(Tag.objects.count(), 3)
