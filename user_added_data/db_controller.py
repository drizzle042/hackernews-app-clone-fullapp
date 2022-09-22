from datetime import datetime, timedelta
import json
import jwt
from itertools import chain
from django.db.utils import IntegrityError
from concurrent.futures import ThreadPoolExecutor
from django.core.paginator import Paginator
from django.conf import settings
from django.db.models import Q
from django.core.exceptions import ObjectDoesNotExist
from django.core.serializers import serialize
from requests import get
from hacker_news_generated_data.models import News
from user_added_data.models import User, UserPosts

HN_URL = "https://hacker-news.firebaseio.com"

class Queries():

    def articles(paginate=10, page=1, **kwargs):

        def queryset(type, keyword):
            if type != "all" and keyword != "null":
                hacker_news_queryset = News.objects.order_by("-time").exclude(type__icontains="comment").filter(Q(type__icontains = type), Q(title__icontains = keyword) | Q(text__icontains = keyword) | Q(by__icontains = keyword))
                user_posts_queryset = UserPosts.objects.order_by("-time").exclude(type__icontains="comment").filter(Q(type__icontains = type), Q(title__icontains = keyword) | Q(text__icontains = keyword))

                queryset = chain(hacker_news_queryset, user_posts_queryset)
                queryset = sorted(
                    queryset,
                    key=lambda i: i.time,
                    reverse=True
                )
                return queryset

            elif type == "all" and keyword != "null":
                hacker_news_queryset = News.objects.order_by("-time").exclude(type__icontains="comment").filter(Q(title__icontains = keyword) | Q(text__icontains = keyword) | Q(by__icontains = keyword))
                user_posts_queryset = UserPosts.objects.order_by("-time").exclude(type__icontains="comment").filter(Q(title__icontains = keyword) | Q(text__icontains = keyword))

                queryset = chain(hacker_news_queryset, user_posts_queryset)
                queryset = sorted(
                    queryset,
                    key=lambda i: i.time,
                    reverse=True
                )
                return queryset

            elif type != "all" and keyword == "null":
                hacker_news_queryset = News.objects.order_by("-time").exclude(type__icontains="comment").filter(Q(type__icontains = type))
                user_posts_queryset = UserPosts.objects.order_by("-time").exclude(type__icontains="comment").filter(Q(type__icontains = type))

                queryset = chain(hacker_news_queryset, user_posts_queryset)
                queryset = sorted(
                    queryset,
                    key=lambda i: i.time,
                    reverse=True
                )
                return queryset

            elif type == "all" and keyword == "null":
                hacker_news_queryset = News.objects.order_by("-time").exclude(type__icontains="comment")
                user_posts_queryset = UserPosts.objects.order_by("-time").exclude(type__icontains="comment")

                queryset = chain(hacker_news_queryset, user_posts_queryset)
                queryset = sorted(
                    queryset,
                    key=lambda i: i.time,
                    reverse=True
                )
                return queryset

        article_type = str(kwargs["type"]).lower()
        search_keyword = str(kwargs["keyword"]).lower()

        paginator = Paginator(queryset(type=article_type, keyword=search_keyword), paginate)
        data = serialize(
            "json",
            paginator.page(page).object_list, 
            use_natural_foreign_keys=True, 
            use_natural_primary_keys=True, 
            fields=(
                "title", 
                "type", 
                "by", 
                "time", 
                "text", 
                "parent", 
                "poll",
                "url",
                "score",
                "kids"
            ))

        return data, paginator

    def comments(id):

        def story(commentID) -> dict:

            if int(commentID) > 100000000000:
                try:
                    queryset = UserPosts.objects.filter(id = int(commentID))
                    querysetSerialized = serialize(
                        "json",
                        queryset,
                        use_natural_foreign_keys=True, 
                        use_natural_primary_keys=True, 
                        fields=(
                            "title", 
                            "type", 
                            "by", 
                            "time", 
                            "text", 
                            "url",
                            "score",
                            "kids"
                        ))
                    data = json.loads(querysetSerialized)
                    return data

                except ObjectDoesNotExist:
                    return ObjectDoesNotExist

            else:
                try:
                    response = get(f"{HN_URL}/v0/item/{commentID}.json")
                    data = [json.loads(response.text)]
                    return data

                except:
                    raise ConnectionError


        parentComment = story(id)

        data = []
        def getComments(commentID):
            data.append(story(commentID))

        with ThreadPoolExecutor(max_workers=20) as executor:
            try:
                for commentID in parentComment[0]["kids"]:
                    executor.submit(getComments, commentID)

                return parentComment, data

            except KeyError:
                return parentComment, data
                
            except TypeError:
                return parentComment, data


class AccountControl():      

    def get_user(data: dict):

        queryset = User.objects.filter(**data)

        if len(queryset) != 0:
            return queryset
        else:
            raise ObjectDoesNotExist

            
    def get_user_model_object(data: dict):

        try:
            queryset = User.objects.get(**data)
            return queryset

        except ObjectDoesNotExist:
            raise ObjectDoesNotExist


    def createAccount(account_data: dict) -> str:

        try:
            user = User(**account_data)
            user.save()
        except IntegrityError:
            raise IntegrityError

        key = settings.SECRET_KEY

        expiration_time = datetime.utcnow() + timedelta(hours=8)
        auth_data = {
            "email": account_data["email"],
            "password": account_data["password"],
            "exp": expiration_time
        }
        auth_token = jwt.encode(payload=auth_data, key=key)

        return auth_token


    def updateAccount(email: str, password: str, data: dict):

        queryset = User.objects.filter(email=email, password=password)

        try:
            if len(queryset) != 0:
                queryset.update(**data)
            else:
                raise ObjectDoesNotExist
                
        except IntegrityError:
            raise IntegrityError  

        
class UserRelatedQueries():

    def get_user_posts(paginate=10, page=1, **kwargs):

        def queryset(user, type, keyword):
            
            if type != "all" and keyword != "null":
                queryset = UserPosts.objects.order_by("-time").exclude(type__icontains="comment").filter(Q(by = user), Q(type__icontains = type), Q(title__icontains = keyword) | Q(text__icontains = keyword))
                return queryset
            elif type == "all" and keyword != "null":
                queryset = UserPosts.objects.order_by("-time").exclude(type__icontains="comment").filter(Q(by = user), Q(title__icontains = keyword) | Q(text__icontains = keyword))
                return queryset
            elif type != "all" and keyword == "null":
                queryset = UserPosts.objects.order_by("-time").exclude(type__icontains="comment").filter(Q(by = user), Q(type__icontains = type))
                return queryset
            elif type == "all" and keyword == "null":
                queryset = UserPosts.objects.order_by("-time").exclude(type__icontains="comment").filter(Q(by = user))
                return queryset
                

        user = kwargs["user"]
        type = str(kwargs["type"]).lower()
        keyword = str(kwargs["keyword"]).lower()

        paginator = Paginator(queryset(user=user, type=type, keyword=keyword), paginate)

        data = serialize(
            "json",
            paginator.page(page).object_list, 
            use_natural_foreign_keys=True, 
            use_natural_primary_keys=True, 
            fields=(
                "title", 
                "type", 
                "by", 
                "time", 
                "text", 
                "url",
                "score",
                "kids"
            ))

        return data, paginator        

    
    def create_user_post(data: dict):
        
        post = UserPosts(**data)
        post.save()


    def delete_user_post(**kwargs):

        user = kwargs["user"]
        post_to_delete = kwargs["post_to_delete"]
        post_to_delete = int(post_to_delete)

        try:
            queryset = UserPosts.objects.get(by=user, id=post_to_delete)
            queryset.delete()
        except ObjectDoesNotExist:
            raise ObjectDoesNotExist

