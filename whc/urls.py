from django.contrib import admin
from django.conf.urls.i18n import i18n_patterns
from django.urls import path, include
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from django.conf import settings
from django.conf.urls.static import static

def trigger_error(request):
    division_by_zero = 1 / 0


schema_view = get_schema_view(
   openapi.Info(
      title="White Bridge Club API",
      default_version="v1",
      contact=openapi.Contact(email="uktamforjob@gmail.com"),
   ),
   public=True,
   permission_classes=[permissions.AllowAny],
)


urlpatterns = [
    path("api/", include("api.urls")),
    path("swagger/", schema_view.with_ui("swagger", cache_timeout=0), name="schema-swagger-ui"),
    path("summernote/", include("django_summernote.urls")),
    # path("sentry-debug/", trigger_error),
    path("rosetta/", include("rosetta.urls")),
    path("i18n/", include("django.conf.urls.i18n")),
]

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

urlpatterns += i18n_patterns(
    path("admin/", admin.site.urls),
)