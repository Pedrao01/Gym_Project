from rest_framework import serializers
from .models import User
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer, AuthUser, Token


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(min_length=8, write_only=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'phone_number', 'password']
        extra_kwargs = {
            'is_staff': {'read_only': True}
        }


class UpdateUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'email', 'phone_number']


class MyTokenSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user: AuthUser) -> Token:

        token = super().get_token(user)

        token['is_staff'] = user.is_staff

        return token