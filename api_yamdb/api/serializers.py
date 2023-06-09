import datetime as dt
import re

from rest_framework import serializers, validators
from rest_framework.generics import get_object_or_404
from rest_framework.exceptions import ValidationError

from reviews.models import (CustomUser,
                            Category,
                            Comment,
                            Genre,
                            Review,
                            Title)


class CategorySerializer(serializers.ModelSerializer):
    """Сериализатор для категорий."""

    class Meta:
        model = Category
        fields = ('name', 'slug')


class GenreSerializer(serializers.ModelSerializer):
    """Сериализатор для жанров."""

    class Meta:
        model = Genre
        fields = ('name', 'slug')


class TitleSerializer(serializers.ModelSerializer):
    """Сериализатор для произведений."""
    rating = serializers.IntegerField(read_only=True)
    category = CategorySerializer()
    genre = GenreSerializer(many=True)

    class Meta:
        model = Title
        fields = (
            'id', 'name', 'year', 'rating', 'description', 'category', 'genre'
        )


class TitleCreateSerializer(serializers.ModelSerializer):
    """Сериализатор для создания произведений."""
    category = serializers.SlugRelatedField(
        queryset=Category.objects.all(),
        slug_field='slug',
        required=True
    )
    # Не нашли других вариантов для поля category
    # (в т.ч. чтобы устраивало пайтест).
    # По redoc в сериализатор нужно передать именно слаг категории,
    # причем поле должно быть доступно на запись.
    # Буду благодарен, если подскажешь, как еще это можно сделать

    genre = serializers.SlugRelatedField(
        queryset=Genre.objects.all(),
        slug_field='slug',
        required=True,
        many=True
    )

    class Meta:
        model = Title
        fields = ('id', 'name', 'year', 'description', 'category', 'genre')

    def validate_year(self, value):
        if value > dt.datetime.now().year:
            raise serializers.ValidationError(
                'Машину времени еще не изобрели!'
            )
        return value

    validators = [
        validators.UniqueTogetherValidator(
            queryset=Title.objects.all(),
            fields=['name', 'year', 'category']
        )
    ]


class ReviewSerializer(serializers.ModelSerializer):
    """Сериализатор для отзывов к произведениям."""
    author = serializers.SlugRelatedField(
        default=serializers.CurrentUserDefault(),
        slug_field='username',
        read_only=True
    )

    class Meta:
        model = Review
        fields = ('id', 'text', 'score', 'author', 'pub_date')

    def validate(self, data):
        request = self.context['request']
        author = request.user
        title = get_object_or_404(
            Title, pk=self.context['view'].kwargs.get('title_id')
        )
        if request.method == 'POST':
            if Review.objects.filter(title=title, author=author):
                raise ValidationError('Можно оставить только один отзыв')
        return data


class CommentSerializer(serializers.ModelSerializer):
    """Сериализатор для комментариев к отзывам."""
    author = serializers.SlugRelatedField(
        slug_field='username', read_only=True
    )

    class Meta:
        model = Comment
        fields = ('id', 'text', 'author', 'pub_date')


class UserRegistrationSerializer(serializers.Serializer):
    """Сериализатор для создания пользователя."""
    username = serializers.CharField(max_length=150, required=True)
    email = serializers.EmailField(max_length=254, required=True)

    def validate_username(self, data):
        username = data
        email = self.initial_data.get('email')
        if username == 'me':
            raise serializers.ValidationError("Имя 'me' запрещено")
        if not re.match(r'^[\w.@+-]+$', username):
            raise serializers.ValidationError(
                f'Некорректный формат введенного логина: {username}.'
            )
        if (CustomUser.objects.filter(
            username=username) and not CustomUser.objects.filter(
                email=email)) or (CustomUser.objects.filter(
                email=email) and not CustomUser.objects.filter(
                username=username)):
            raise serializers.ValidationError(
                "Пользователь зарегистрирован с другими данными."
            )
        return data


class TokenSerializer(serializers.ModelSerializer):
    """Сериализатор для получения токена."""
    username = serializers.SlugField(max_length=150, required=True)
    confirmation_code = serializers.IntegerField(required=True)

    class Meta:
        model = CustomUser
        fields = ('username', 'confirmation_code')


class AdminUserDetailSerializer(serializers.ModelSerializer):
    """Сериализатор для создания пользователя админом."""
    username = serializers.SlugField(max_length=150, required=True)
    email = serializers.EmailField(max_length=254, required=True)
    first_name = serializers.CharField(max_length=150, required=False)
    last_name = serializers.CharField(max_length=150, required=False)
    bio = serializers.CharField(required=False)
    role = serializers.ChoiceField(
        required=False,
        choices=CustomUser.ROLE_CHOICES,
        default=CustomUser.USER,
    )

    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'first_name',
                  'last_name', 'bio', 'role')

    def validate_username(self, value):
        """Проверяет, что имя не 'me' и оно не занято."""
        if value == 'me':
            raise serializers.ValidationError("Имя 'me' запрещено")
        if CustomUser.objects.filter(username=value).exists():
            raise serializers.ValidationError(f"Имя {value} занято")
        return value

    def validate_email(self, value):
        """Проверяет, что указанный адрес почты не занят."""
        if CustomUser.objects.filter(email=value).exists():
            raise serializers.ValidationError(
                "На этот адрес эл. почты уже зарегистрирован аккаунт."
            )
        return value


class UserDetailSerializer(serializers.ModelSerializer):
    """Сериализатор для редактирования и просмотра профиля пользователя."""
    username = serializers.SlugField(max_length=150, required=True)
    email = serializers.EmailField(max_length=254, required=True)
    first_name = serializers.CharField(max_length=150, required=False)
    last_name = serializers.CharField(max_length=150, required=False)
    bio = serializers.CharField(required=False)

    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'first_name',
                  'last_name', 'bio', 'role')
        read_only_fields = ('role',)
