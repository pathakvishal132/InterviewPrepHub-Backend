from rest_framework import serializers
from .models import Questions


class SpeechSerializer(serializers.ModelSerializer):
    class Meta:
        model = Questions
        fields = ("id", "speech_text", "language")
