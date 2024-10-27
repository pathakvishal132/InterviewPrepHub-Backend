from django.db import models


class Speech(models.Model):
    speech_text = models.TextField()
    language = models.CharField(max_length=20)
    unique_phrase = models.CharField(max_length=200, default="")
    mostFrequentWord = models.CharField(max_length=200, default="")
