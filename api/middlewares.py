from django.utils.deprecation import MiddlewareMixin

from .utils import get_lang


class LanguageHeaderMiddleware(MiddlewareMixin):
    """Language middleware custom."""
    def process_request(self, request):
        request.query_params = {}
        request.query_params["lang"] = request.GET.get("lang", "uz")
        request.META["Accept-language"] = get_lang(request)
        response = self.get_response(request)
        return response