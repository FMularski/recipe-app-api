"""
    Serializers for recipe api.
"""
from core.models import Recipe, Tag
from rest_framework import serializers


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = (
            "id",
            "name",
        )
        read_only_fields = ("id",)


class RecipeSerializer(serializers.ModelSerializer):
    """Serialzier for Recipe model"""

    tags = TagSerializer(many=True, required=False)

    class Meta:
        model = Recipe
        fields = ["id", "title", "time_minutes", "price", "link", "tags"]
        read_only_fields = ("id",)

    def create(self, validated_data):
        tags = validated_data.pop("tags", [])
        recipe = Recipe.objects.create(**validated_data)
        user = self.context["request"].user

        for tag_params in tags:
            tag, created = Tag.objects.get_or_create(
                user=user,
                **tag_params,
            )
            recipe.tags.add(tag)

        return recipe


class RecipeDetailSerializer(serializers.ModelSerializer):
    """Serializer for Recipe detail view"""

    tags = TagSerializer(many=True, required=False)

    class Meta:
        model = Recipe
        fields = RecipeSerializer.Meta.fields + ["description"]

    def _get_or_create_tags(self, tags, recipe):
        """Handle getting or creating tags as needed."""
        user = self.context["request"].user
        for tag_params in tags:
            tag, created = Tag.objects.get_or_create(
                user=user,
                **tag_params,
            )
            recipe.tags.add(tag)

    def update(self, instance, validated_data):
        """Update recipe."""
        tags = validated_data.pop("tags", None)
        if tags is not None:
            instance.tags.clear()
            self._get_or_create_tags(tags, instance)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()

        return instance
