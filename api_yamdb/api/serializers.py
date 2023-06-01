import datetime as dt

from django.db.models import Avg
from rest_framework import serializers

from reviews.models import Category, Genre, Title


class CategorySerializer(serializers.ModelSerializer):

    class Meta:
        model = Category
        fields = ('id', 'name', 'slug')


class GenreSerializer(serializers.ModelSerializer):

    class Meta:
        model = Genre
        fields = ('id', 'name', 'slug')


class TitleSerializer(serializers.ModelSerializer):
    year = serializers.IntegerField()
    rating = serializers.SerializerMethodField(read_only=True)
    category = CategorySerializer()
    genre = GenreSerializer(many=True)

    class Meta:
        model = Title
        fields = ('id', 'name', 'year', 'rating', 'description', 'category', 'genre')

    def validate_year(self, value):
        if value > dt.datetime.now().year:
            raise serializers.ValidationError(
                'Машину времени еще не изобрели!'
            )
        return value

    def get_rating(self, obj):
        return obj.reviews.aggregate(Avg('score'))
        # нужно поле 'title' c related_name 'reviews' в модели Reviews
