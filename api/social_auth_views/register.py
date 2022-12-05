import os
import urllib3
from django.contrib.auth import authenticate
from django.db import transaction
from io import StringIO
from api.models import Profile, User
from rest_framework.exceptions import AuthenticationFailed
from django.core.files import File


def register_social_user(provider, user_id, email, name, image_url=None):
    filtered_user_by_email = User.objects.filter(email=email)
    if filtered_user_by_email.exists():
        if provider == filtered_user_by_email[0].provider:
            registered_user = authenticate(
                email=email,
                password=os.environ.get("SOCIAL_SECRET")
            )
            tokens = registered_user.tokens()
        else:
            tokens = filtered_user_by_email[0].tokens()
        return tokens
    else:
        user = {
            "email": email,
            "password": os.environ.get("SOCIAL_SECRET")
        }
        with transaction.atomic():
            user = User.objects.create_user(**user)
            user.provider = provider
            user.save()
            profile = {
                "fullname": name,
                "user": user
            }
            profile = Profile(**profile)
            if image_url:
                try:
                    s = StringIO()
                    s.write(urllib3.urlopen(image_url).read())
                    s.size = s.tell()
                    profile.photo.save("test.jpg", File(s), save=False)
                except Exception as e:
                    print(e)
            profile.save()
        new_user = authenticate(
            email=email,
            password=os.environ.get("SOCIAL_SECRET")
        )
        return new_user.tokens()