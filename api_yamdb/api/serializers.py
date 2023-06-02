from rest_framework import serializers
from reviews.models import CustomUser, ConfirmationCode


class UserRegistrationSerializer(serializers.ModelSerializer):
    """Сериализатор для отправки кода через email."""
    email = serializers.EmailField(max_length=254, required=True)
    username = serializers.SlugField(max_length=150, required=True)

    class Meta:
        model = CustomUser
        fields = ('username', 'email')

    def validate_username(self, value):
        """Проверяет, что имя не 'me'."""
        if value == 'me':
            raise serializers.ValidationError("Имя 'me' запрещено")


class UserConfirmationSerializer(serializers.Serializer):
    """Сериализатор для регистрации пользователя."""
    username = serializers.SlugField(max_length=150, required=True)
    confirmation_code = serializers.CharField(required=True)

    def validate_confirmation_code(self, value):
        """Проверяет, что код соответствует отправленному."""
        if value != ConfirmationCode.objects.last():
            raise serializers.ValidationError("Неправильный код")


class UserCreationSerializer(serializers.ModelSerializer):
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
