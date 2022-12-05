from django.conf import settings
from django.utils.translation import get_language_from_request
from .utils import get_lang

class TranslatedSerializerMixin(object):
    def to_representation(self, instance):
        inst_rep = super().to_representation(instance)
        request = self.context.get("request", None) or self.request
        lang_code = get_lang(request)
        result = {}
        for field_name, field in self.get_fields().items():
            if field_name != "translations":
                field_value = inst_rep.pop(field_name)
                result.update({field_name: field_value})
            if field_name == "translations":
                translations = inst_rep.pop(field_name)
                if lang_code not in translations:
                    parler_default_settings = settings.PARLER_LANGUAGES["default"]
                    if "fallback" in parler_default_settings:
                        lang_code = parler_default_settings.get("fallback")
                    if "fallbacks" in parler_default_settings:
                        lang_code = parler_default_settings.get("fallbacks")[0]
                for lang, translation_fields in translations.items():
                    if lang == lang_code:
                        trans_rep = translation_fields.copy()
                        for trans_field_name, trans_field in translation_fields.items():
                            field_value = trans_rep.pop(trans_field_name)
                            result.update({trans_field_name: field_value})

        return result


class SuperUserEditableFieldsMixin:
    def get_readonly_fields(self, request, obj=None):
        if request.user.is_superuser:
            return []
        return self.readonly_fields


class AdminUserCannotDeleteMixin:
    def has_add_permission(self, request, obj=None):
        if request.user.is_superuser:
            return True
        return False