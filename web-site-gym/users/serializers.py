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