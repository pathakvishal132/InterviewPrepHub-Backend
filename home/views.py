from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import *
from .serializers import *
from django.conf import settings
from django.http import JsonResponse


api_key = settings.API_KEY


@api_view(["GET"])
def get_speeches(request):
    try:
        speeches = Speech.objects.all()
        serializer = SpeechSerializer(speeches, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Exception as e:
        return Response(str(e), status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(["POST"])
def create_speech(request):
    """
    Create a new speech object.
    """
    try:
        # Validate and create the speech object using the serializer
        serializer = SpeechSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response(str(e), status=status.HTTP_500_INTERNAL_SERVER_ERROR)
