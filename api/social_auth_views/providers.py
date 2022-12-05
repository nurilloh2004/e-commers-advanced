from google.auth.transport import requests
from google.oauth2 import id_token
import facebook


class Google:
    @staticmethod
    def validate(auth_token):
        try:
            idinfo = id_token.verify_oauth2_token(
                auth_token,
                requests.Request()
            )

            if "accounts.google.com" in idinfo["iss"]:
                return idinfo

        except:
            return "The token is either invalid or has expired"


class Facebook:
    @staticmethod
    def validate(auth_token):
        try:
            graph = facebook.GraphAPI(access_token=auth_token)
            profile = graph.request("/me?fields=name,email,picture")
            return profile
        except:
            return "The token is invalid or expired."