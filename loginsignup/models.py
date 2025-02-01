from django.db import models


# Create your models here.
class UploadedImage(models.Model):
    img_id = models.CharField(max_length=255, default="default_id")
    name = models.CharField(max_length=255)
    image_data = models.BinaryField()
