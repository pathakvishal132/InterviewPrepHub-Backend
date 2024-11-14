from django.db import models


# class Speech(models.Model):
#     speech_text = models.TextField()
#     language = models.CharField(max_length=20)
#     unique_phrase = models.CharField(max_length=200, default="")
#     mostFrequentWord = models.CharField(max_length=200, default="")
class Email(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} <{self.email}>"
