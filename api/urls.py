from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

from api.views import *


router = DefaultRouter()
router.register("profile", ProfileCreateUpdateViewSet, basename="profile")
router.register("entities", EntityViewSet, basename="entities")
router.register("categories", CategoryViewSet, basename="categories")
router.register("view", EntityViewCreateViewSet, basename="view")
router.register("banner-click", BannerClickCreateViewSet, basename="banner-click")
router.register("like", EntityLikeCreateViewSet, basename="like")
router.register("email-list", EmailListCreateViewSet, basename="email-list")
router.register("banners", BannerListViewSet, basename="banners")
router.register("genders", GenderListViewSet, basename="genders")
router.register("countries", CountryViewSet, basename="countries")
router.register("translations", StaticTranslationListViewSet, basename="translations")
router.register("contact-links", ContactLinkListViewSet, basename="contact-links")
router.register("share-links", ShareLinkListViewSet, basename="share-links")
router.register("crypto-content", CryptoContentListViewSet, basename="crypto-content")
router.register("static-pages", StaticPageListViewSet, basename="static-pages")
router.register('orders', OrderViewSet, basename="orders")
# router.register("auth", SocialAuthViewSet, basename="auth")


urlpatterns = [
    path("partners/", PartnerListView.as_view()),

    path('entity/list/', EntityListApiView.as_view()),
    path('api/entity-detail/<int:pk>/', EntityDetailAPIView.as_view(), name='entity_detail'),
    path("google/", GoogleSocialAuthView.as_view()),
    path("facebook/", FacebookSocialAuthView.as_view()),

    path("test/", test),
    path("email-list-file/", email_list_file_view, name="email-list-file"),

    path("token/", TokenObtainPairView.as_view()),
    path("token/refresh/", TokenRefreshView.as_view()),

    path("user/activate/", UserProfileActivationAPIView.as_view()),

    path("", include(router.urls)),
]
