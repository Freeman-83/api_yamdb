import datetime as dt
from django.db.models import Avg
from rest_framework import serializers, validators

from rest_framework.exceptions import ValidationError
from rest_framework.generics import get_object_or_404
from reviews.models import (Category,
                            Genre,
                            Title,
                            Comment,
                            Review,
                            CustomUser,
                            ConfirmationCode)


class CategorySerializer(serializers.ModelSerializer):

    class Meta:
        model = Category
        fields = ('name', 'slug')


class GenreSerializer(serializers.ModelSerializer):

    class Meta:
        model = Genre
        fields = ('name', 'slug')


class TitleSerializer(serializers.ModelSerializer):
    rating = serializers.SerializerMethodField(read_only=True)
    category = CategorySerializer()
    genre = GenreSerializer(many=True)

    class Meta:
        model = Title
        fields = (
            'id', 'name', 'year', 'rating', 'description', 'category', 'genre'
        )

    def get_rating(self, obj):
        rating = obj.reviews.aggregate(Avg('score'))
        return rating['score__avg']


class TitleCreateSerializer(serializers.ModelSerializer):
    category = serializers.SlugRelatedField(
        queryset=Category.objects.all(),
        slug_field='slug',
        required=True
    )
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
    author = serializers.SlugRelatedField(
        slug_field='username', read_only=True
    )

    class Meta:
        model = Comment
        fields = ('id', 'text', 'author', 'pub_date')


class EmailSerializer(serializers.ModelSerializer):
    """Сериализатор для отправки кода через email."""
    username = serializers.SlugField(max_length=150, required=True)
    email = serializers.EmailField(max_length=254, required=True)

    class Meta:
        model = CustomUser
        fields = ('username', 'email')

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


class TokenSerializer(serializers.Serializer):
    """Сериализатор для получения токена."""
    username = serializers.SlugField(max_length=150, required=True)
    confirmation_code = serializers.CharField(required=True)

    def validate_confirmation_code(self, value):
        """Проверяет, что код соответствует отправленному."""
        if value != ConfirmationCode.objects.last().confirmation_code:
            raise serializers.ValidationError("Неправильный код")
        return value


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


class UserDetail(serializers.ModelSerializer):
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
