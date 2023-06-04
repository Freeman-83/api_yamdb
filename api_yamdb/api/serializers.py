from rest_framework import serializers
from reviews.models import CustomUser, ConfirmationCode


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
                "На этот адрес эл. почты уже зарегистрирован аккаунт.")


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
    first_name = serializers.CharField(max_length=150, required=False)
    last_name = serializers.CharField(max_length=150, required=False)
    bio = serializers.CharField(required=False)
    role = serializers.ChoiceField(
        required=False,
        choices=CustomUser.ROLE_CHOICES,
        default=CustomUser.USER)

    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'first_name',
                  'last_name', 'bio', 'role')
        validators = [serializers.UniqueTogetherValidator(
            queryset=CustomUser.objects.all(),
            fields=['username', 'email']
        )]


class UserDetail(serializers.ModelSerializer):
    """Сериализатор для редактирования и просмотра профиля пользователя."""
    first_name = serializers.CharField(max_length=150, required=False)
    last_name = serializers.CharField(max_length=150, required=False)
    bio = serializers.CharField(required=False)

    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'first_name',
                  'last_name', 'bio')
        validators = [serializers.UniqueTogetherValidator(
            queryset=CustomUser.objects.all(),
            fields=['username', 'email']
        )]
