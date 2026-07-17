"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from users.views import UserView, CreateUserViews, MyTokenObtainPairView
from plans.views import PlanView, PaymentConfirmView, PlanStatusView, PlanCancelView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('gym/create-user/', CreateUserViews.as_view()),
    path('gym/user/', UserView.as_view()),
    path('gym/login/', MyTokenObtainPairView.as_view()),
    path('gym/refresh/', TokenRefreshView.as_view()),
    path('gym/plan-payment/', PlanView.as_view()),
    path('gym/payments/confirm/', PaymentConfirmView.as_view()),
    path('gym/payments/status/', PlanStatusView.as_view()),
    path('gym/plan/cancel/', PlanCancelView.as_view())
]
