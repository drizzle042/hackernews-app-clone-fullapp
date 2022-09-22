import json
from urllib import response
import jwt
from jwt.exceptions import DecodeError, ExpiredSignatureError
from django.db.utils import IntegrityError
from datetime import datetime, timedelta
from django.core.exceptions import ObjectDoesNotExist
from django.core.serializers import serialize
from django.conf import settings
from django.views import View
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from .db_controller import AccountControl, Queries, UserRelatedQueries


payload = {
    "totalDocs" : 0,
    "totalPages" : 0,
    "page": 1,
    "data": None
}

user_signup_data = {
    "name": "",
    "email": "",
    "password": ""
}

user_to_get_payload = {
    "email": "",
    "password": ""    
}

users_post = {
    "title": "",
    "type": "",
    "text": "",
    "url": "",
}


class AllArticles(View):

    def get(self, request):

        # Query params
        params = request.GET
        page = params.get("page") if params.get("page") else  1
        paginate = params.get("limit") if params.get("limit") else  10
        type = params.get("type") if params.get("type") else  "all"
        keyword = params.get("keyword") if params.get("keyword") else "null"

        # Query
        query = Queries.articles(paginate = paginate, page = page, type = type, keyword = keyword)
        
        # Payload
        payload["totalDocs"] = query[1].count
        payload["totalPages"] = query[1].num_pages
        payload["page"] = page
        payload["data"] = json.loads(query[0])

        return JsonResponse(payload)


class Comments(View):

    def get(self, request):
        # Query params
        params = request.GET

        if params.get("commentid"):
            id = params.get("commentid")  

        else:
            response = JsonResponse({
                "status": "Error", 
                "message": "The comment ID is a required field"
                })
            response.status_code = 400
            response.reason_phrase = "comment ID is a required field to see comment"

            return response

        # Query 
        try:
            query = Queries.comments(id = id)

        except ConnectionError:
            response = JsonResponse({
                    "status": "Server Down", 
                    "message": "The News server is down at the moment"
                    })
            response.status_code = 500
            response.reason_phrase = "The News server is down at the moment"

            return response

        except ObjectDoesNotExist:
            response = JsonResponse({
                    "status": "Not Found", 
                    "message": "Oops the comment you tried to view couldn't be found. It seemes it has been deleted."
                    })
            response.status_code = 404
            response.reason_phrase = "Not Found"

            return response

        # Payload
        payload["totalDocs"] = len(query[1])
        payload["data"] = {
            "parent": query[0],
            "comments": query[1]
            }

        return JsonResponse(payload)


@method_decorator(csrf_exempt, name="dispatch")
class Account(View):

    def decode_auth_token(self, token: str):

        # decode JSON web token
        key = settings.SECRET_KEY

        try:
            decoded_token = jwt.decode(token, key=key, algorithms=["HS256"], verify=True)

            return decoded_token

        except DecodeError:
            response = JsonResponse({
                "status": "Couldn't authenticate",
                "message": "Authorization required. You are unauthorized. The problem could be that your auth token is missing or has been tampered with. To get a new token, signin."
            })
            response.status_code = 401
            response.reason_phrase = "We couldn't verify you"

            return response

        except ExpiredSignatureError:
            response = JsonResponse({
                "status": "Couldn't authenticate",
                "message": "Authorization required. You are unauthorized. Your auth token has expired. To get a new token, signin."
            })
            response.status_code = 401
            response.reason_phrase = "We couldn't verify you"

            return response


    def get(self, request):
        
        request_header = request.headers
        
        token = str(request_header["authorization"]).split()[1]
        decoded_token = self.decode_auth_token(token=token)
        
        if type(decoded_token) == dict:
            decoded_email = decoded_token["email"]
            decoded_password = decoded_token["password"]
        else: 
            return decoded_token
        
        user_to_get_payload["email"] = decoded_email
        user_to_get_payload["password"] = decoded_password

        try:
            user = AccountControl.get_user(user_to_get_payload)
            user_json = serialize("json", user)

            response = HttpResponse(user_json)
            response.headers = {
                "Content-Type": "application/json"
            }

            return response

        except ObjectDoesNotExist:
            response = JsonResponse({
                "status": "Oops. Not found",
                "message": "The account you are looking for could not be found. Maybe should you should ckeck Mars lol. Don't mind me, the account does not exist. Check the email and password again."
            })
            response.status_code = 404

            return response


    def post(self, request):

        request = json.loads(request.body)
        # Params
        firstName = request["firstName"] if "firstName" in request else ""
        lastName = request["lastName"] if "lastName" in request else ""
        fullName = f"{firstName} {lastName}"

        try:
            email = request["email"]
            password = request["password"]
        except KeyError:
            response = JsonResponse({
                    "status": "Bad request. Missing fields are required!", 
                    "message": "User email and password are required. If you missed any of these, please provide. This might be a mistake, it happens, lol."
                    })
            response.status_code = 400
            response.reason_phrase = "Bad request. Missing fields are required!"

            return response

        user_signup_data["name"] = str(fullName).strip()
        user_signup_data["email"] = email
        user_signup_data["password"] = password

        # Store request and return auth token
        try:
            response = AccountControl.createAccount(user_signup_data)

        except IntegrityError:
            response = JsonResponse({
                    "status": "Bad request. User already exists!", 
                    "message": "An account has already been created with this email. If this was you, don't worry just sign in."
                    })
            response.status_code = 400
            response.reason_phrase = "Bad request. User already exists!"

            return response

        return JsonResponse({
            "authToken": response,
            "message": "Account was successfully created",
            "status": "Success"
        })
        
    
    def put(self, request):

        request_header = request.headers
        request = json.loads(request.body)

        token = str(request_header["authorization"]).split()[1]
        decoded_token = self.decode_auth_token(token=token)

        if type(decoded_token) == dict:
            decoded_email = decoded_token["email"]
            decoded_password = decoded_token["password"]
        else: 
            return decoded_token

        # Params
        firstName = request["firstName"] if "firstName" in request else ""
        lastName = request["lastName"] if "lastName" in request else ""
        email = request["email"] if "email" in request else decoded_email
        password = request["password"] if "password" in request else decoded_password
        fullName = f"{firstName} {lastName}"

        user_signup_data["name"] = str(fullName).strip()
        user_signup_data["email"] = email
        user_signup_data["password"] = password

        try:
            AccountControl.updateAccount(email=decoded_email, password=decoded_password, data=user_signup_data)

            response = JsonResponse({
                "status": "Success",
                "message": "Account updated successfully. To continue using the app, please signin."
            })

            return response

        except ObjectDoesNotExist:
            response = JsonResponse({
                "status": "Bad request",
                "message": "The account you want to update could not be found!"
            })
            response.status_code = 400

            return response
            
        except IntegrityError:
            response = JsonResponse({
                    "status": "Bad request. User already exists!", 
                    "message": "The email you tried to sign up with already exists. Emails are usually unique so trace your steps back to know where the problem lies."
                    })
            response.status_code = 400
            response.reason_phrase = "Bad request. User already exists!"

            return response



@method_decorator(csrf_exempt, name="dispatch")
class SignIn(View):

    def post(self, request):

        request = json.loads(request.body)

        try:
            email = request["email"]
            password = request["password"]
        except KeyError:
            response = JsonResponse({
                    "status": "Bad request. Missing fields are required!", 
                    "message": "User email and password are required. If you missed any of these, please provide. This might be a mistake, it happens, lol."
                    })
            response.status_code = 400
            response.reason_phrase = "Bad request. Missing fields are required!"

            return response

        user_to_get_payload["email"] = email
        user_to_get_payload["password"] = password    

        try:
            user = AccountControl.get_user(user_to_get_payload)
            account_data = user.values()[0]

            key = settings.SECRET_KEY
            expiration_time = datetime.utcnow() + timedelta(hours=8)
            auth_data = {
                "email": account_data["email"],
                "password": account_data["password"],
                "exp": expiration_time
            }
            auth_token = jwt.encode(payload=auth_data, key=key)

            return JsonResponse({
                "authToken": auth_token,
                "message": "You have been signed in successfully",
                "status": "Success"
            })

        except ObjectDoesNotExist:
            response = JsonResponse({
                "status": "Couldn't authenticate",
                "message": "Couldn't signin. Please check your email and password then try again."
            })
            response.status_code = 406
            response.reason_phrase = "Couldn't authenticate"

            return response

            
@method_decorator(csrf_exempt, name="dispatch")
class UserRelatedActivities(View):

    def get(self, request):
        
        # Params
        request_header = request.headers
        
        token = str(request_header["authorization"]).split()[1]
        decoded_token = Account().decode_auth_token(token=token)
        
        if type(decoded_token) == dict:
            decoded_email = decoded_token["email"]
            decoded_password = decoded_token["password"]
        else: 
            return decoded_token
        
        user_to_get_payload["email"] = decoded_email
        user_to_get_payload["password"] = decoded_password
        
        try:
            # To get the current active user
            user = AccountControl.get_user_model_object(user_to_get_payload)

        except ObjectDoesNotExist:
            response = JsonResponse({
                "status": "Forbidden. Couldn't authenticate",
                "message": "We could not find any posts that belong to you because we could not recognize you. Try signin back in or create a new account."
            })
            response.status_code = 403
            response.reason_phrase = "You are not authenticated so you can't see your posts. Please signin."

            return response

        # Params
        params = request.GET
        page = params.get("page") if params.get("page") else  1
        paginate = params.get("limit") if params.get("limit") else  10
        article_type = params.get("type") if params.get("type") else  "all"
        keyword = params.get("keyword") if params.get("keyword") else "null"

        # Query
        query = UserRelatedQueries.get_user_posts(paginate = paginate, page = page, user=user, type = article_type, keyword = keyword)
        
        # Payload
        payload["totalDocs"] = query[1].count
        payload["totalPages"] = query[1].num_pages
        payload["page"] = page
        payload["data"] = json.loads(query[0])

        return JsonResponse(payload)


    def post(self, request):

        request_header = request.headers
        request_body = json.loads(request.body)
        
        token = str(request_header["authorization"]).split()[1]
        decoded_token = Account().decode_auth_token(token=token)
        
        if type(decoded_token) == dict:
            decoded_email = decoded_token["email"]
            decoded_password = decoded_token["password"]
        else: 
            return decoded_token
        
        user_to_get_payload["email"] = decoded_email
        user_to_get_payload["password"] = decoded_password
        
        # Params
        text = request_body["text"] if "text" in request_body else ""
        url = request_body["url"] if "url" in request_body else ""

        try:
            title = request_body["title"]
            article_type = request_body["type"]
        except KeyError:
            response = JsonResponse({
                    "status": "Bad request. Missing fields are required!", 
                    "message": "Article title and type are required. If you missed any of these, please provide. This might be a mistake, it happens, lol."
                    })
            response.status_code = 400
            response.reason_phrase = "Bad request. Missing fields are required!"

            return response

        users_post["title"] = title
        users_post["type"] = article_type
        users_post["text"] = text
        users_post["url"] = url
        
        try:
            # To create a new UserPosts
            user = AccountControl.get_user_model_object(user_to_get_payload)
            post = {
                "by": user,
            }
            post.update(users_post)

            UserRelatedQueries.create_user_post(data=post)
            
            response = JsonResponse({
                "status": "Success",
                "message": "You have successfully made a new post. You can view it in your browser."
            })

            return response


        except ObjectDoesNotExist:
            response = JsonResponse({
                "status": "Forbidden. Couldn't authenticate",
                "message": "You do not have rights to post articles at the moment because we could not recognize you. Try signin back in or create a new account."
            })
            response.status_code = 403
            response.reason_phrase = "You are not allowed to do this. Please signin."

            return response


    def delete(self, request):
    
        request_header = request.headers
        request_body = json.loads(request.body)

        token = str(request_header["authorization"]).split()[1]
        decoded_token = Account().decode_auth_token(token=token)
        
        if type(decoded_token) == dict:
            decoded_email = decoded_token["email"]
            decoded_password = decoded_token["password"]
        else: 
            return decoded_token
        
        user_to_get_payload["email"] = decoded_email
        user_to_get_payload["password"] = decoded_password
        
        try:
            # To get the current active user
            user = AccountControl.get_user_model_object(user_to_get_payload)

            
        except ObjectDoesNotExist:
            response = JsonResponse({
                "status": "Forbidden. Couldn't authenticate",
                "message": "We could not find any posts that belong to you because we could not recognize you. Try signin back in or create a new account."
            })
            response.status_code = 403
            response.reason_phrase = "You are not allowed to be here. Please signin."

            return response

        # Params
        try:
            post_id = request_body["id"]
        except KeyError:
            response = JsonResponse({
                    "status": "Bad request. Missing id. The object ID to delete is required!", 
                    "message": "The ID of the object to delete is required. If you missed it, please provide. This might be a mistake, it happens, lol."
                    })
            response.status_code = 400
            response.reason_phrase = "Bad request. Missing required object ID!"

            return response

        try:
            # Query
            UserRelatedQueries.delete_user_post(user=user, post_to_delete=post_id)
            response = JsonResponse({
                "status": "Success",
                "message": f"The article with ID {post_id} has been permanently deleted."
            })

            return response

        except ObjectDoesNotExist:
            response = JsonResponse({
                "status": "The article to delete could not be found.",
                "message": "We could not find any post with that ID that belongs to you."
            })
            response.status_code = 404

            return response

