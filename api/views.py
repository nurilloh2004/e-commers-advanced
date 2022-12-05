from django.http import HttpResponseRedirect
from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.viewsets import GenericViewSet, mixins
from rest_framework.decorators import action
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework import status
from django.conf import settings
from django.db.models import Count, Q
from django.utils import timezone
from django.db import transaction
from django.shortcuts import get_object_or_404

from api.models import *
from api.pagination import *
from api.serializers import *
from api.utils import *
from api.social_auth_views.views import *
from api.func_views import *


class CategoryViewSet(
        mixins.ListModelMixin,
        GenericViewSet
    ):
    queryset = Category.objects.root_nodes()
    serializer_class = CategorySerializer

    @action(detail=True, methods=["get"], url_path="common-terms")
    def common_searched_terms(self, request, pk=None):
        self.ip = get_ip_address(self.request)
        data = get_country_code_from_ip(self.ip)
        queryset = SearchTerm.objects.filter(category__id=pk)
        if data["status"]:
            queryset = queryset.filter(country=data["country_code"])
        serializer = SearchTermSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class UserProfileActivationAPIView(APIView):
    def get(self, request):
        params = request.query_params
        otp = OTP.objects.filter(email=params["email"], code=params["code"], expires_in__gt=timezone.now()).first()

        if not otp:
            return HttpResponse("Expired link :(")

        otp.is_activated = True
        otp.save()

        user = User.objects.filter(email=otp.email).first()
        if not user:
            return HttpResponse("User not exists :(")

        user.is_active = True
        user.save()
        tokens = user.tokens()
        print(tokens)
        return HttpResponseRedirect(redirect_to="https://whitebridge.club/login" \
            .format(tokens['access'], tokens['refresh']))



class ProfileCreateUpdateViewSet(
        mixins.CreateModelMixin,
        mixins.UpdateModelMixin,
        mixins.RetrieveModelMixin,
        GenericViewSet
    ):
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer
    redis = settings.REDIS_OBJ

    def retrieve(self, request, pk=None):
        profile = Profile.objects.filter(user__id=pk)
        if not profile.exists():
            return Response(status=status.HTTP_404_NOT_FOUND)
        profile = profile.first()
        serializer = self.serializer_class(profile)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = self.perform_create(serializer)
        token = RefreshToken.for_user(user)
        data = {
            "refresh": str(token),
            "access": str(token.access_token),
            "refreshToken": str(token),
            "accessToken": str(token.access_token),
        }
        return Response(data, status=201)

    def perform_create(self, serializer):
        with transaction.atomic():
            profile = serializer.save()
            email = profile.user.email
            code = generate_code(k=15)
            OTP.objects.create(email=email, code=code, expires_in=timezone.now() + timezone.timedelta(days=1))
            activation_link = "https://whitebridge.site/api/user/activate/?email={}&code={}".format(email, code)
            send_confirmation_email(activation_link, email)
            return profile
        return None


    def update(self, request, pk=None):
        instance = Profile.objects.get(id=pk)
        data = {**request.data}
        user = data.pop("user", None)
        if user:
            email = user.get("email", None)
            if email:
                instance.user.email = email
                instance.user.save()
        gender_id = data.pop("gender", None)
        if gender_id:
            gender = Gender.objects.get(id=gender_id)
            instance.gender = gender
            instance.user.save()
        for key in data.keys():
            if key == "photo":
                photo = data["photo"][0]
                instance.photo.save(photo.name, photo)
            elif hasattr(instance, key):
                setattr(instance, key, data[key])
        instance.save()
        serializer = self.serializer_class(instance)
        return Response(serializer.data, status=status.HTTP_200_OK)


    @action(detail=False, methods=["post"], url_path="reset-password1")
    def reset_password1(self, request):
        user = User.objects.filter(email=request.data["email"])
        if user.exists():
            user = user.first()
            code = generate_code()
            OTP.objects.create(
                email=user.email,
                code=code,
                expires_in=timezone.now() + timezone.timedelta(minutes=2)
            )
            send_welcome_email("Password recovery", "Code: {}".format(code), [user.email])
            return Response(status=status.HTTP_200_OK)
        else:
            return Response(status=status.HTTP_404_NOT_FOUND)


    @action(detail=False, methods=["post"], url_path="reset-password2")
    def reset_password2(self, request):
         user = User.objects.filter(email=request.data["email"])
         print(request.POST.get("code",None))
#	print(request.POST.get("code", None))

#	print(f"User -------> {user}")
         print(request.POST.get("email", None))
         if user.exists():
             user = user.first()
             otp = OTP.objects.filter(
                 email=user.email,
                 code=request.data["code"],
                 expires_in__gt=timezone.now(),
                 is_activated=True
             ).first()
             if otp:
                 return Response(status=status.HTTP_200_OK)
             else:
                 return Response(status=status.HTTP_400_BAD_REQUEST)
         else:
             return Response(status=status.HTTP_404_NOT_FOUND)


    @action(detail=False, methods=["post"], url_path="reset-password3")
    def reset_password3(self, request):
        user = User.objects.filter(email=request.data["email"])
        if user.exists():
            user = user.first()
            otp = OTP.objects.filter(
                email=user.email,
                code=request.data["code"],
                is_active=True
            ).first()
            if otp:
                otp.is_active = False
                otp.save()
                user.set_password(str(request.data["password"]))
                user.save()
                return Response(status=status.HTTP_200_OK)
            else:
                return Response(status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(status=status.HTTP_404_NOT_FOUND)


    @action(detail=False, methods=["post"], url_path="change-password")
    def change_password(self, request):
        data = request.data
        user_id = data.get("user_id", None)
        if not user_id:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        old_password = data.get("old_password", None)
        if not old_password:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        new_password = data.get("new_password", None)
        if not new_password:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        user = User.objects.filter(id=user_id)
        if not user.exists():
            return Response(status=status.HTTP_404_NOT_FOUND)
        else:
            user = user.first()
            if not user.check_password(old_password):
                return Response(status=status.HTTP_401_UNAUTHORIZED)
            user.set_password(new_password)
            user.save()
        return Response(status=status.HTTP_200_OK)


class EntityListApiView(ListAPIView):
    serializer_class = EntitySerializer
    queryset = Entity.objects.all()
    def get_queryset(self):
        self.ip = get_ip_address(self.request)
        self.country = get_country(self.request, self.ip)
        self.queryset = self.queryset.filter(links__country__in=[self.country, "all"])
        return self.queryset


class EntityViewSet(
        mixins.ListModelMixin,
	    mixins.RetrieveModelMixin,
        GenericViewSet
    ):
    serializer_class = EntitySerializer
    queryset = Entity.objects.all()
    pagination_class = EntityPagination
    authentication_classes = []
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        self.ip = get_ip_address(self.request)
        self.country = get_country(self.request, self.ip)
        self.queryset = self.queryset.filter(links__country__in=[self.country, "all"])
        self.queryset = self.apply_filters(self.queryset, self.request)
        return self.queryset


    def get_serializer_context(self):
        context = super().get_serializer_context()
        return {
            **context,
            "ip": self.ip,
            "country": self.country
        }


    def apply_filters(self, queryset, request):
        data = request.GET

        term = data.get("term", None)
        if term and queryset.exists():
            result_by_term = queryset.filter(
                Q(title__contains=term) |
                Q(translations__description__contains=term)
            )
            words = term.split()
            if len(words) > 1:
                result_by_word = queryset.filter(
                    Q(title__in=words) |
                    Q(translations__description__in=words)
                )
                queryset = result_by_term | result_by_word
            else:
                queryset = result_by_term

            if queryset.exists():
                save_search_term(term, queryset, request)

        return queryset


    def return_paginated_response(self, queryset, request, *args, **kwargs):
        context = {"request": request, "ip": self.ip, "country": self.country}
        category_data = kwargs.get("category_data", None)
        paginator = self.pagination_class()
        if category_data:
            paginator.category_data = category_data
        page = paginator.paginate_queryset(queryset, request)
        if page is not None:
            serializer = self.serializer_class(page, many=True, context=context)
            return paginator.get_paginated_response(serializer.data)
        serializer = self.serializer_class(queryset, many=True, context=context)
        return Response(serializer.data)


    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        queryset = queryset.filter(expires_in__gte=timezone.now()).order_by("-created_at")
        return self.return_paginated_response(queryset, request)


    @action(detail=False, methods=["get"], url_path="most-liked")
    def most_liked(self, request):
        queryset = self.get_queryset()
        queryset = queryset.annotate(likes_count=Count("likes")) \
            .order_by("-likes_count")
        return self.return_paginated_response(queryset, request)


    @action(detail=False, methods=["get"], url_path="most-viewed")
    def most_viewed(self, request):
        queryset = self.get_queryset()
        queryset = queryset.annotate(views_count=Count("views")) \
            .order_by("-views_count")
        return self.return_paginated_response(queryset, request)


    @action(detail=False, methods=["get"], url_path="latest")
    def latest(self, request):
        queryset = self.get_queryset()
        queryset = queryset.order_by("-created_at")
        return self.return_paginated_response(queryset, request)

    @action(detail=False, methods=["get"], url_path="allentities")
    def allentities(self, request):
        ip1 = get_ip_address(self.request)
        country = get_country(self.request, ip1)
        queryset = self.queryset.filter(links__country__in=[country, "all"])
        serializer = self.serializer_class(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["get"], url_path="home")
    def home(self, request):
        self.ip = get_ip_address(self.request)
        self.country = get_country(self.request, self.ip)
        if hasattr(request.user, "profile"):
            profile = Profile.objects.get(id=request.user.profile.id)
            if not profile.country_code or profile.country_code.isupper():
                try:
                    profile.country_code = self.country
                    profile.save()
                except:
                    pass
        context = {"request": request, "ip": self.ip, "country": self.country}
        categories = Category.objects.language(get_lang(request)).all()
        result = []
        for category in categories:
            entities = self.get_queryset().filter(category=category) \
                .distinct().annotate(views_count=Count("views")) \
                .order_by("-views_count")
            serializer = self.serializer_class(
                entities,
                many=True,
                context=context
            )
            item = {
                "category": {
                    "id": category.id,
                    "title": category.title
                },
                "count": entities.count(),
                "results": [*serializer.data]
            }
            result.append(item)
        return Response(result, status=status.HTTP_200_OK)


    @action(detail=True, methods=["get"], url_path="per-category")
    def per_category(self, request, pk=None):
        category = Category.objects.get(id=pk)
        queryset = self.get_queryset().filter(category=category, expires_in__gte = timezone.now()).distinct()
        queryset = queryset.order_by("-created_at")

        data = {
            "id": category.id,
            "title": category.title,
	}
        return self.return_paginated_response(queryset,request,category_data=data)

class EntityDetailAPIView(RetrieveAPIView):
    serializer_class = EntitySerializer
    queryset = Entity.objects.all()

    def get_queryset(self):
        self.ip = get_ip_address(self.request)
        self.country = get_country(self.request, self.ip)
        self.queryset = self.queryset.filter(links__country__in=[self.country, "all"])
        self.queryset = self.apply_filters(self.queryset, self.request)
        return self.queryset

    def apply_filters(self, queryset, request):
        data = request.GET

        term = data.get("term", None)
        if term and queryset.exists():
            result_by_term = queryset.filter(
                Q(title__contains=term) |
                Q(translations__description__contains=term)
            )
            words = term.split()
            if len(words) > 1:
                result_by_word = queryset.filter(
                    Q(title__in=words) |
                    Q(translations__description__in=words)
                )
                queryset = result_by_term | result_by_word
            else:
                queryset = result_by_term

            if queryset.exists():
                save_search_term(term, queryset, request)

        return queryset

class PartnerListView(ListAPIView):
    queryset = Partner.objects.all()
    serializer_class = PartnerSerializer


class EntityViewCreateViewSet(
        mixins.CreateModelMixin,
        GenericViewSet
    ):
    queryset = View.objects.all()
    serializer_class = ViewSerializer
    authentication_classes = [JWTAuthentication]

    def create(self, request):
        request_serializer = self.serializer_class(data=request.data)
        if request_serializer.is_valid():
            locatable_data = get_locatable_data(request)
            view = request_serializer.save(
                **locatable_data,
                profile = request.user.profile
            )
            serializer = self.serializer_class(view)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(status=status.HTTP_400_BAD_REQUEST)

    def perform_update(self, serializer):

        user1 = self.request.user
        view1 = View.objects.filter(profile__user = user1).count()

        serializer.save(view1_count=view1)

class BannerClickCreateViewSet(
        mixins.CreateModelMixin,
        GenericViewSet
    ):
    queryset = BannerClick.objects.all()
    serializer_class = BannerClickSerializer
    authentication_classes = [JWTAuthentication]

    def create(self, request):
        request_serializer = self.serializer_class(data=request.data)
        if request_serializer.is_valid():
            locatable_data = get_locatable_data(request)
            view = request_serializer.save(**locatable_data)
            serializer = self.serializer_class(view)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(status=status.HTTP_400_BAD_REQUEST)


class EntityLikeCreateViewSet(
        mixins.CreateModelMixin,
        mixins.DestroyModelMixin,
        GenericViewSet
    ):
    queryset = Like.objects.all()
    serializer_class = LikeSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        request_serializer = self.serializer_class(data=request.data)
        if request_serializer.is_valid():
            queryset = self.get_queryset().filter(
                profile = request.user.profile,
                entity = request.data["entity"]
            )
            if not queryset.exists():
                locatable_data = get_locatable_data(request)
                like = request_serializer.save(
                    **locatable_data,
                    profile = request.user.profile
                )
                serializer = self.serializer_class(like)
            else:
                serializer = self.serializer_class(queryset.first())
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(status=status.HTTP_400_BAD_REQUEST)


class EmailListCreateViewSet(
        mixins.CreateModelMixin,
        GenericViewSet
    ):
    queryset = SubscribeEmail.objects.all()
    serializer_class = SubscribeEmailSerializer

    def create(self, request, *args, **kwargs):
        request_serializer = self.serializer_class(data=request.data)
        if request_serializer.is_valid():
            queryset = SubscribeEmail.objects.filter(email=request.data["email"])
            if not queryset.exists():
                locatable_data = get_locatable_data(request)
                email_obj = request_serializer.save(**locatable_data)
                serializer = self.serializer_class(email_obj)
            else:
                serializer = self.serializer_class(queryset.first())
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(status=status.HTTP_400_BAD_REQUEST)


class BannerListViewSet(
        mixins.ListModelMixin,
        GenericViewSet
    ):
    queryset = Banner.objects.all()
    serializer_class = BannerSerializer

    def get_queryset(self):
        self.ip = get_ip_address(self.request)
        self.country = get_country(self.request, self.ip)
        self.queryset = self.queryset.filter(country__in=[self.country, "all"])
        return self.queryset


    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.serializer_class(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


    @action(detail=True, methods=["get"], url_path="per-category")
    def per_category(self, request, pk=None):
        queryset = self.get_queryset().filter(category__id=pk)
        serializer = self.serializer_class(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class CountryViewSet(GenericViewSet):
    serializer_class = CountrySerializer

    @action(detail=False, methods=["get"], url_path="list")
    def countries_list(self, request):
        from django_countries import countries
        self.ip = get_ip_address(self.request)
        self.country = get_country(request, self.ip)
        result = {
            "current": {},
            "others": []
        }
        for country in countries:
            result["others"].append({
                "title": country.name,
                "flag": get_country_flag(country.code),
                "code": country.code.lower()
            })
            if country.code.lower() == self.country:
                result["current"] = {
                    "title": country.name,
                    "flag": get_country_flag(country.code),
                    "code": country.code.lower()
                }
        return Response(result, status=status.HTTP_200_OK)


    @action(detail=False, methods=["get"], url_path="languages")
    def languages(self, request):
        from django.conf import settings
        self.lang = get_lang(request)
        current_language = list(filter(lambda x: x["code"] == self.lang, settings.LANGS))[0]
        result = {
            "current": current_language,
            "others": settings.LANGS
        }
        return Response(result, status=status.HTTP_200_OK)

    @action(detail=False, methods=["get"], url_path="current")
    def current(self, request):
        self.ip = get_ip_address(self.request)
        self.country = get_country(request, self.ip)
        self.result = get_captial_location(self.country)
        return Response(
            self.result,
            status=status.HTTP_200_OK
        )


class StaticTranslationListViewSet(
        mixins.ListModelMixin,
        GenericViewSet
    ):
    serializer_class = StaticTranslationSerializer
    queryset = StaticTranslation.objects.all()
    authentication_classes = []
    permission_classes = []

    def get_queryset(self):
        return self.queryset.all()

    def list(self, request):
        queryset = self.get_queryset()
        serializer = self.serializer_class(
            queryset,
            many=True,
            context={
                "request": request,
                "lang": get_lang(request)
            }
        )
        data = [*serializer.data]
        result = {}
        for item in data:
            result[item["key"]] = item["value"]
        return Response(result, status=status.HTTP_200_OK)


class ContactLinkListViewSet(
        mixins.ListModelMixin,
        GenericViewSet
    ):
    serializer_class = ContactLinkSerializer
    queryset = ContactLink.objects.all()
    authentication_classes = []
    permission_classes = []

    def get_queryset(self):
        self.ip = get_ip_address(self.request)
        self.country = get_country(self.request, self.ip)
        self.queryset = self.queryset.filter(links__country__in=[self.country, "all"]).distinct()
        return self.queryset


    def get_serializer_context(self):
        return {
            **super().get_serializer_context(),
            "country": self.country
        }


class ShareLinkListViewSet(
        mixins.ListModelMixin,
        GenericViewSet
    ):
    serializer_class = ShareLinkSerializer
    queryset = ShareLink.objects.all()
    authentication_classes = []
    permission_classes = []

    @action(detail=False, methods=["get"], url_path="referal-stats")
    def referal_stats(self, request):
        user = request.user
        if user.is_anonymous:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        referals = Referal.objects.filter(referencer=user)
        sources = [*self.queryset.all()]
        result = {}
        for referal in referals:
            for source in sources:
                if referal.source == source.slug:
                    if source.slug in list(result.keys()):
                        result[source.slug]["count"] += 1
                    else:
                        result[source.slug] = {
                            "title": source.title,
                            "slug": source.slug,
                            "count": 1
                        }
        return Response(result, status=status.HTTP_200_OK)


class CryptoContentListViewSet(
        mixins.ListModelMixin,
        GenericViewSet
    ):
    serializer_class = CryptoContentSerializer
    queryset = CryptoContent.objects.all()
    authentication_classes = []
    permission_classes = []


class GenderListViewSet(
        mixins.ListModelMixin,
        GenericViewSet
    ):
    serializer_class = GenderSerializer
    queryset = Gender.objects.all()
    authentication_classes = []
    permission_classes = []


class StaticPageListViewSet(
        mixins.ListModelMixin,
        mixins.RetrieveModelMixin,
        GenericViewSet
    ):
    serializer_class = StaticPageSerializer
    queryset = StaticPage.objects.all()
    authentication_classes = []
    permission_classes = []


    def retrieve(self, request, pk=None, **kwargs):
        static_page = StaticPage.objects.filter(slug=pk)
        if static_page.exists():
            static_page = static_page.first()
            serializer = self.serializer_class(static_page, context={"request": request})
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(status=status.HTTP_404_NOT_FOUND)


class AdminStatisticsViewSet(GenericViewSet):
    pass




from rest_framework import (
    viewsets,
    mixins,
    status,
)
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated


class OrderViewSet(mixins.DestroyModelMixin,
                   mixins.UpdateModelMixin,
                   mixins.ListModelMixin,
                   mixins.CreateModelMixin,
                   viewsets.GenericViewSet):
    """Order view set view."""
    # authentication_classes = [TokenAuthentication]
    serializer_class = OrderSerializer
    queryset = Order.objects.all()
