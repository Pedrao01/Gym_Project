from rest_framework import serializers
from .models import User
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer, AuthUser, Token
from plans.serializers import PlanSerializer


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(min_length=8, write_only=True)
    plan = PlanSerializer(read_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'phone_number', 'password', 'plan']
        extra_kwargs = {
            'is_staff': {'read_only': True}
        }


class UpdateUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'email', 'phone_number']

    def validate_your_fields_name(self, username, email, phone_number):
        current_user = self.context['request'].user

        exists = User.objects.filter(
            username=username, email=email, phone_number=phone_number
        ).exclude(pk=current_user.id).exists()

        if exists:
            raise serializers.ValidationError('This data already exists in the database.')

        return username, email, phone_number


class MyTokenSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user: AuthUser) -> Token:

        token = super().get_token(user)

        token['is_staff'] = user.is_staff

        return token


class StatsSerializer(serializers.ModelSerializer):
    total = serializers.IntegerField(read_only=True)
    with_plan = serializers.IntegerField(read_only=True)
    without_plan = serializers.IntegerField(read_only=True)