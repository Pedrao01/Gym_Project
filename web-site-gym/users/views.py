from django.shortcuts import render
from django.core.exceptions import ValidationError
from rest_framework.views import APIView, Response, status
from .serializers import UserSerializer, UpdateUserSerializer, MyTokenSerializer
from .services import creates_user, get_by_username, update_user, update_user_plan
from rest_framework.permissions import AllowAny, IsAdminUser
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework import generics
from rest_framework.filters import SearchFilter
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.pagination import PageNumberPagination

from .models import User
from plans.models import Plan

# Create your views here.


class CreateUserViews(APIView):
    permission_classes = [AllowAny]

    def post(self, request) -> Response:

        serializer = UserSerializer(data=request.data)

        if not serializer.is_valid():
            return Response({'error': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = creates_user(**serializer.validated_data)

            return Response({
                'user_id': user.id,
                'email': user.email
            }, status=status.HTTP_201_CREATED)

        except ValidationError as e:
            return Response({'errors': e.message}, status=status.HTTP_400_BAD_REQUEST)

        except Exception:
            return Response({'error': 'Internal Server Error'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class UserView(APIView):
    def get(self, request) -> Response:
        username = request.user.username
        user = get_by_username(username)
        user_serializer = UserSerializer(user)

        return Response(user_serializer.data, status=status.HTTP_200_OK)

    def patch(self, request) -> Response:
        user = request.user

        serializer = UpdateUserSerializer(
            instance=user,
            data=request.data,
            partial=True
        )

        if serializer.is_valid():
            update = update_user(user, **serializer.validated_data)

            return Response({
                'new data': update,
            }, status=status.HTTP_200_OK)

        return Response({}, status=status.HTTP_400_BAD_REQUEST)


#  Rota: gym/login/
class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenSerializer


class StatsView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        plans = Plan.objects.all()
        total = len(plans)
        with_plan = len(plans.filter(is_active=True))
        without_plan = len(plans.filter(is_active=False))

        return Response({
            'total': total,
            'with_plan': with_plan,
            'without_plan': without_plan
        }, status=status.HTTP_200_OK)


class ListUsersView(generics.ListAPIView):
    serializer_class = UserSerializer
    permission_classes = [IsAdminUser]
    filter_backends = [DjangoFilterBackend, SearchFilter]
    search_fields = ['username', 'email', 'phone_number']

    def get_queryset(self):
        queryset = User.objects.filter(plan__isnull=False).select_related('plan').order_by('id')

        return queryset


class UpdatePlanUserView(generics.UpdateAPIView):
    permission_classes = [IsAdminUser]

    def patch(self, request, *args, **kwargs):
        if not kwargs:
            return Response({'error': 'You must send user id in the route parameters'},
                            status=status.HTTP_400_BAD_REQUEST)
        if 'is_active' not in request.data:
            return Response({'error': "You must send 'is_active' in the body"},
                            status=status.HTTP_400_BAD_REQUEST)
        if not isinstance(request.data['is_active'], bool):
            return Response({'error': 'is_active must be bool'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            user = update_user_plan(kwargs['user_id'], request.data['is_active'])
            serializer = UserSerializer(user)

            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': e.args}, status.HTTP_400_BAD_REQUEST)