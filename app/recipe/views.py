"""
    Views for the recipe APIs.
"""
from core.models import Ingredient, Recipe, Tag
from recipe import serializers
from rest_framework import mixins, viewsets
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated


class RecipeViewSet(viewsets.ModelViewSet):
    """View for manage recipe APIs."""

    queryset = Recipe.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Return queryset of recipes based on the authenticated user."""
        return Recipe.objects.all().filter(user=self.request.user).order_by("-id")

    def get_serializer_class(self):
        """Return recipe serializer based on the performed action."""
        if self.action in ["list", "create"]:
            return serializers.RecipeSerializer

        return serializers.RecipeDetailSerializer

    def perform_create(self, serializer):
        """Create a new recipe."""
        serializer.save(user=self.request.user)


class TagViewSet(
    mixins.ListModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    """Manage Tag objects."""

    serializer_class = serializers.TagSerializer
    queryset = Tag.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Return the user's tags."""
        return self.queryset.filter(user=self.request.user).order_by("-name")


class IngredientViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    """Manage ingredients in the database."""

    serializer_class = serializers.IngredientSerializer
    queryset = Ingredient.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Filter queryset by the user."""
        return self.queryset.filter(user=self.request.user).order_by("-name")
