from uuid import uuid1
from django.db import models
from django.db.models.deletion import CASCADE
from hacker_news_generated_data.models import NewsBaseClass



def createID():
    id = uuid1().int >> 64
    id = id / 2.5
    return abs(int(id))



class User(models.Model):
    id = models.BigAutoField(primary_key=True, unique=True, default=createID)
    name = models.CharField(max_length=150, null=True, blank=True)
    email = models.EmailField(unique=True)
    password = models.TextField(serialize=False)
    date_created = models.DateTimeField(auto_now_add=True)


    def natural_key(self):
        return (self.name)
    
    def __str__(self) -> str:
        return self.name


class UserPosts(NewsBaseClass):
    id = models.BigAutoField(primary_key=True, unique=True, default=createID)
    by = models.ForeignKey(to=User, on_delete=CASCADE)
    time = models.DateTimeField(blank=True, null=True, auto_now_add=True)

    def __str__(self) -> str:
        return super().title
