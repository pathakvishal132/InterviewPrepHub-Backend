from rest_framework import serializers
from .models import Speech


class SpeechSerializer(serializers.ModelSerializer):
    class Meta:
        model = Speech
        fields = ("id", "speech_text", "language")
