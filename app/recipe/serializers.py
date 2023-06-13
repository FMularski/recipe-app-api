"""
    Serializers for recipe api.
"""
from core.models import Recipe, Tag
from rest_framework import serializers


class RecipeSerializer(serializers.ModelSerializer):
    """Serialzier for Recipe model"""

    class Meta:
        model = Recipe
        fields = ["id", "title", "time_minutes", "price", "link"]
        read_only_fields = ("id",)


class RecipeDetailSerializer(serializers.ModelSerializer):
    """Serializer for Recipe detail view"""

    class Meta:
        model = Recipe
        fields = RecipeSerializer.Meta.fields + ["description"]


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = (
            "id",
            "name",
        )
        read_only_fields = ("id",)
