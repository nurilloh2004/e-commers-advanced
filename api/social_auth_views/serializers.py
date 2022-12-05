import os

import facebook
from rest_framework import serializers
from rest_framework.exceptions import AuthenticationFailed

from api.social_auth_views.register import register_social_user
from . import providers


class GoogleSocialAuthSerializer(serializers.Serializer):
    auth_token = serializers.CharField()

    def validate_auth_token(self, auth_token):
        user_data = providers.Google.validate(auth_token)

        try:
            user_data["sub"]
        except:
            raise serializers.ValidationError(
                "The token is invalid or expired. Please login again."
            )

        if user_data["aud"] != os.environ.get("GOOGLE_OAUTH2_CLIENT_ID"):

            raise AuthenticationFailed("oops, who are you?")

        user_id = user_data["sub"]
        email = user_data["email"]
        name = user_data["name"]
        provider = "google"

        return register_social_user(
            provider=provider,
            user_id=user_id,
            email=email,
            name=name
        )


class FacebookSocialAuthSerializer(serializers.Serializer):
    auth_token = serializers.CharField()

    def validate_auth_token(self, auth_token):
        user_data = providers.Facebook.validate(auth_token)

        try:
            user_id = user_data["id"]
            email = user_data.get("email", None)
            if not email:
                email = user_id + "@wbt.club"
            name = user_data["name"]
            provider = "facebook"
            return register_social_user(
                provider=provider,
                user_id=user_id,
                email=email,
                name=name
            )
        except Exception as identifier:
            raise serializers.ValidationError(
                "The token is invalid or expired. Please login again."
            )