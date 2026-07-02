from django.shortcuts import render
from django.core.exceptions import ValidationError
from rest_framework.views import APIView, Response, status
from .serializers import UserSerializer, UpdateUserSerializer
from .services import creates_user, get_by_username, update_user
from rest_framework.permissions import AllowAny

# Create your views here.


class CreateUserViews(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        try:
            username = request.user
            users = get_by_username(username=username)
            serializer = UserSerializer(users)

            return Response(serializer.data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({'errors': e.args})

    def post(self, request) -> Response:

        serializer = UserSerializer(data=request.data)

        if not serializer.is_valid():
            return Response({'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = creates_user(**serializer.validated_data)

            return Response({
                'user_id': user.id,
                'email': user.email
            }, status=status.HTTP_201_CREATED)

        except ValidationError as e:
            return Response({'errors': e.message}, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            print(e.args)


class UserView(APIView):
    def get(self, request) -> Response:
        username = request.user.username
        user = get_by_username(username)
        user_serializer = UserSerializer(user)

        return Response(user_serializer.data, status=status.HTTP_201_CREATED)

    def patch(self, request) -> Response:
        user_id = request.user.id

        serializer = UpdateUserSerializer(data=request.data)

        if serializer.is_valid():
            update = update_user(user_id, **serializer.validated_data)

            return Response({
                'new data': update,
            }, status=status.HTTP_200_OK)
