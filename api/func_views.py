from django.http import HttpResponse, HttpResponseNotFound
from django.contrib.admin.views.decorators import staff_member_required

from api.models import Profile


def test(request):
    """Test function."""
    from .tasks import test_func
    test_func.delay()
    return HttpResponse("Done!")


@staff_member_required
def email_list_file_view(request):
    try:
        country_code = request.GET.get("country_code__exact", None)
        email_list = Profile.objects.filter(
            country_code__iexact=country_code
        ).values_list(
            "user__email",
            flat=True
        )
        data = ",".join(email_list)
        response = HttpResponse(data, content_type="text/plain")
        response["Content-Disposition"] = 'attachment; filename="email-list.txt"'

    except IOError:
        response = HttpResponseNotFound("<h1>Could not generate email list</h1>")

    return response