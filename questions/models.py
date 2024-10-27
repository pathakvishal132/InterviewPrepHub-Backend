from django.db import models


class Questions(models.Model):
    question = models.CharField(max_length=2000)
    domain = models.CharField(max_length=200)
    subdomain = models.CharField(max_length=200, default="")
    answer = models.TextField()
