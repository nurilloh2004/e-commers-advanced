from rest_framework.response import Response
from rest_framework.generics import GenericAPIView
from rest_framework import status

from .serializers import FacebookSocialAuthSerializer, GoogleSocialAuthSerializer


class GoogleSocialAuthView(GenericAPIView):
    serializer_class = GoogleSocialAuthSerializer

    def post(self, request):
        try:
            request.data["auth_token"] = request.data["tokenObj"]["id_token"]
            serializer = self.serializer_class(data=request.data)
            serializer.is_valid(raise_exception=True)
            data = ((serializer.validated_data)["auth_token"])
            return Response(data, status=status.HTTP_200_OK)
        except Exception as e:
            print(e)
            return Response(status=status.HTTP_400_BAD_REQUEST)


class FacebookSocialAuthView(GenericAPIView):
    serializer_class = FacebookSocialAuthSerializer

    def post(self, request):
        try:
            # should be changed
            request.data["auth_token"] = request.data["accessToken"]
            # should be changed

            serializer = self.serializer_class(data=request.data)
            serializer.is_valid(raise_exception=True)
            data = ((serializer.validated_data)["auth_token"])
            return Response(data, status=status.HTTP_200_OK)
        except Exception as e:
            print(e)
            return Response(status=status.HTTP_400_BAD_REQUEST)