import os
import json
import random
import requests as r

from django.conf import settings
from django.core.mail import send_mail
from googletrans import Translator


translator = Translator()


def send_otp_email():
    pass

def generate_otp_code():
    return "AB123"


def get_ip_address(request):    
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded_for:
        ip = x_forwarded_for.split(",")[0]
    else:
        ip = request.META.get("REMOTE_ADDR")
    return ip


def get_country_code_from_ip(ip):
    url = f"http://ip-api.com/json/{ip}"
    response = r.get(url)
    if 200 <= response.status_code < 300:
        data = json.loads(response.content)
        status = data.get("status", None)
        if status == "fail":
            return {
                "status": False
            }
        return {
            "status": True,
            "country_code": data["countryCode"].lower(),
            "country": data["country"],
            "latitude": data["lat"],
            "longitude": data["lon"]
        }
    return {
        "status": False
    }


def get_device_type(request):
    if request.user_agent.is_mobile:
        return "mobile"
    if request.user_agent.is_tablet:
        return "tablet"
    if request.user_agent.is_touch_capable:
        return "touch_capable"
    if request.user_agent.is_pc:
        return "pc"
    if request.user_agent.is_bot:
        return "bot"
    return "other"


def save_search_term(term, queryset, request):
    from api.models import SearchTerm
    instance = queryset.first().links.first()
    locatable_data = get_locatable_data(request)
    search_term = SearchTerm(
        term=term,
        **locatable_data
    )
    if hasattr(request.user, "profile"):
        search_term.profile = request.user.profile

    if hasattr(instance, "category"):
        search_term.category = instance.category
    search_term.save()
    return search_term


def get_locatable_data(request):
    ip = get_ip_address(request)
    data = get_country_code_from_ip(ip)
    device = get_device_type(request)

    return {
        "ip": ip,
        "country": data["country_code"],
        "device": device
    }


def get_country_flag(country_code):
    return settings.BACKEND_URL + settings.STATIC_URL + "flags/" + country_code.lower() + ".svg"


def get_country(request, ip):
    country = request.query_params.get("country", None)
    if not country:
        data = get_country_code_from_ip(ip)
        if data["status"]:
            country = data["country_code"]
        else:
            country = "en"
    
    if country == "kr":
        country = "ko"

    return country


def get_lang(request):
    lang = request.query_params.get("lang", None)
    if not lang:
        ip = get_ip_address(request)
        data = get_country_code_from_ip(ip)
        if data["status"]:
            lang = data["country_code"]
        else:
            lang = "en"
        if lang == "kr":
            lang = "ko"
    if not lang in settings.COUNTRIES_TO_LANGS.keys():
        chosen = None
        for item in settings.COUNTRIES_TO_LANGS.items():
            if lang in item[1]:
                chosen = item[0]
                break
        if chosen:
            lang = chosen
        else:
            lang = "en"
    return lang


def check_and_save_referal(user, data):
    from api.models import User, Referal
    ref_code = data.get("ref", None)
    source = data.get("source", None)
    if ref_code == "null":
        ref_code = None
    if source == "null":
        source = None
    if ref_code:
        referencer = User.objects.filter(ref_code=ref_code)
        if referencer.exists():
            referencer = referencer.first()
            try:
                referal = Referal(
                    referencer=referencer,
                    referal=user,
                )
                if source:
                    referal.source = source
                referal.save()
            except Exception as e:
                print(e)


def get_obj_link_for_country(obj, country):
    link = None
    print(country)
    if country:
        link = obj.links.filter(country=country).first()
    if not link:
        link = obj.links.filter(country="all").first()
    for item in obj.links.all():
        print(item)
        print(item.country)
        print(item.link)
    if link:
        print(link)
        return link.link
    print("working")
    return ""


def get_captial_location(country):
    file_path = os.path.join(settings.BASE_DIR, "api", "data", "capitals.json")
    file = open(file_path, "r")
    data = json.load(file)
    result = {
        "status": False
    }
    for item in data:
        if item["code"] == country.lower():
            result = item
            result["status"] = True
    else:
        if not result["status"]:
            result["error"] = "Could not find the location"
    return result


def google_translate(text, from_lang_code, to_lang_code):
    translator = Translator()
    result = translator.translate(text, src=from_lang_code, dest=to_lang_code)
    return result.text


def smart_truncate(content, length=50, suffix="..."):
    if len(content) <= length:
        return content
    else:
        return " ".join(content[:length+1].split(" ")[0:-1]) + suffix


def send_welcome_email(subject, message, to=[]):
    send_mail(
        subject=subject,
        message=message,
        from_email=settings.EMAIL_HOST_USER,
        recipient_list=to,
        fail_silently=True
    )


def generate_code(k=5):
    CHARS = "0123456789"
    code = "".join([CHARS[random.randint(0, 9)] for _ in range(k)])
    return code


def send_confirmation_email(link, email):
    text = f"Email confirmation link for White Bridge Club\n\n In order to activate your profile, click on this link ({link})\n\nNote: this link will be expired in 24 hours."
    send_mail(
        subject="Email Confirmation",
        message=text,
        from_email=settings.EMAIL_HOST_USER,
        recipient_list=[email],
        fail_silently=True
    )
