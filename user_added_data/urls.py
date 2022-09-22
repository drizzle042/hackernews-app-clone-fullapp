"""Python_interview_test URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.urls import path
from django.views.generic import TemplateView
from user_added_data.views import AllArticles, Comments, Account, SignIn, UserRelatedActivities

urlpatterns = [
    path("api/v0/account/", Account.as_view(), name="account"),
    path("api/v0/articles/", AllArticles.as_view(), name="allarticles"),
    path("api/v0/comments/", Comments.as_view(), name="comments"),
    path("api/v0/myarticles/", UserRelatedActivities.as_view(), name="user-related-activities"),
    path("api/v0/signin/", SignIn.as_view(), name="signin"),
    path("", TemplateView.as_view(template_name = "index.html"), name="home"),
]