import json
from django.db import models

# Base Class
class NewsBaseClass(models.Model):
    
    id = models.IntegerField(primary_key=True, unique=True)
    by = models.CharField(max_length=200, blank=True, null=True)
    title = models.CharField(max_length=200, null=True)
    type = models.CharField(max_length = 40, null=True)
    time = models.DateTimeField(blank=True, null=True)
    text = models.TextField(blank=True, null=True)
    dead = models.BooleanField(blank=True, default=False, null=True)
    parent = models.IntegerField(unique=True, blank=True, null=True)
    poll = models.IntegerField(unique=True, blank=True, null=True)
    url = models.URLField(blank=True, null=True)
    score = models.IntegerField(blank=True, null=True, default=0)
    descendants = models.IntegerField(blank=True, null=True)
    kids = models.TextField(blank=True, null=True)

    class Meta:
        abstract = True


# Create your models here.
class News(NewsBaseClass):
    def __str__(self) -> str:
        return super().title
