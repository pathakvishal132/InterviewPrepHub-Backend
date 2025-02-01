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
import base64
import os
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.http import JsonResponse
from .models import *
from django.core.exceptions import ValidationError
from django.db import IntegrityError, DatabaseError


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
                    "message": "success",
                    "data": user_serializer.data,
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
            {
                "message": "Welcome to the dashboard",
                # "user": user_serializer.data,
                "id": user_serializer.data.get("id"),
            },
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


@api_view(["POST"])
def upload_image(request):
    if request.method == "POST":
        try:
            # Get the image file and name from the request
            image_file = request.FILES["image"]
            name = request.POST.get("name", "default_name")
            image_id = request.POST.get("id")

            # Read the image file as bytes
            image_bytes = image_file.read()
            try:
                uploaded_image = UploadedImage.objects.filter(img_id=image_id).first()
                if not uploaded_image:
                    uploaded_image_1 = UploadedImage.objects.create(
                        img_id=image_id, name=name, image_data=image_bytes
                    )
                    message = "Image uploaded successfully!"
                    return JsonResponse(
                        {"message": message, "id": uploaded_image_1.img_id}, status=201
                    )
                else:  # If id is not provided, create a new record
                    try:
                        # uploaded_image = UploadedImage.objects.get(img_id=image_id)
                        uploaded_image.name = name
                        uploaded_image.image_data = image_bytes
                        uploaded_image.save()
                        message = "Image updated successfully!"
                    except UploadedImage.DoesNotExist:
                        return JsonResponse(
                            {"error": "Image with the given id does not exist"},
                            status=404,
                        )

                return JsonResponse(
                    {"message": message, "id": uploaded_image.img_id}, status=201
                )
            except (IntegrityError, DatabaseError) as e:
                print(f"Database error: {e}")

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)

    return JsonResponse({"error": "Invalid request method"}, status=405)


@api_view(["GET"])
def get_image(request, image_id):
    try:
        image_record = UploadedImage.objects.get(img_id=image_id)

        # Convert byte array to base64 string
        image_base64 = base64.b64encode(image_record.image_data).decode("utf-8")

        return JsonResponse(
            {"name": image_record.name, "image_base64": image_base64}, status=200
        )
    except UploadedImage.DoesNotExist:
        return JsonResponse({"error": "Image not found"}, status=404)
