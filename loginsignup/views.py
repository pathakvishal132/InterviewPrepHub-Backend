from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view
from django.contrib.auth import authenticate, login
from rest_framework import status
from django.contrib.auth import logout
from django.views.decorators.csrf import csrf_exempt
from rest_framework_simplejwt.tokens import RefreshToken
from django.shortcuts import render
from rest_framework import generics
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.contrib.auth.models import User
from .serializers import RegisterSerializer, LoginSerializer, UserSerializers
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny


class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = RegisterSerializer


class LoginView(generics.GenericAPIView):
    serializer_class = LoginSerializer

    def post(self, request, *args, **kwargs):
        username = request.data.get("username")
        password = request.data.get("password")
        user = authenticate(username=username, password=password)

        if user is not None:
            refresh = RefreshToken.for_user(user)
            user_serializer = UserSerializers(user)
            return Response(
                {
                    "refresh": str(refresh),
                    "access": str(refresh.access_token),
                    "user": user_serializer.data,
                }
            )
        else:
            return Response({"detail": "Invalid credentials"}, status=401)


class DashboardView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        user = request.user
        user_serializer = UserSerializers(user)
        return Response(
            {"message": "Welcome to the dashboard", "user": user_serializer.data},
            status=200,
        )


# # Create your views here.
# @csrf_exempt
# @api_view(["POST"])
# def signup(request):
#     email = request.data.get("email")
#     password = request.data.get("password")
#     confirm_password = request.data.get("confirmPassword")

#     if password != confirm_password:
#         return Response(
#             {"error": "Passwords do not match"}, status=status.HTTP_400_BAD_REQUEST
#         )

#     if User.objects.filter(email=email).exists():
#         return Response(
#             {"error": "Email already exists"}, status=status.HTTP_400_BAD_REQUEST
#         )

#     user = User.objects.create(
#         username=email,  # Using email as username
#         email=email,
#         password=make_password(password),  # Hash the password
#     )
#     return Response(
#         {"message": "User created successfully"}, status=status.HTTP_201_CREATED
#     )


# @csrf_exempt
# @api_view(["POST"])
# def login_view(request):
#     email = request.data.get("email")
#     password = request.data.get("password")

#     user = authenticate(username=email, password=password)
#     if user is not None:
#         login(request, user)
#         return Response({"message": "Login successful"}, status=status.HTTP_200_OK)
#     else:
#         return Response(
#             {"error": "Invalid email or password"}, status=status.HTTP_400_BAD_REQUEST
#         )


# @csrf_exempt
# @api_view(["POST"])
# def logout_view(request):
#     logout(request)
#     return Response({"message": "Logged out successfully"}, status=status.HTTP_200_OK)