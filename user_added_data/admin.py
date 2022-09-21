from django.contrib import admin

from user_added_data.models import User, UserPosts

# Register your models here.
admin.site.register(User)
admin.site.register(UserPosts)