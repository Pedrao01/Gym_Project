from rest_framework import serializers
from rest_framework_simplejwt.serializers import (
    AuthUser,
    Token,
    TokenObtainPairSerializer,
)

from plans.serializers import PlanSerializer

from .models import User


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(min_length=8, write_only=True)
    plan = PlanSerializer(read_only=True)

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "email",
            "phone_number",
            "password",
            "plan",
            "is_staff",
        ]
        extra_kwargs = {"is_staff": {"read_only": True}}


class UpdateUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["username", "email", "phone_number"]


class MyTokenSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user: AuthUser) -> Token:

        token = super().get_token(user)

        token["is_staff"] = user.is_staff

        return token
