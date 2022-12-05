from celery import shared_task


@shared_task(bind=True)
def test_func(self):
    for i in range(10):
        print(i)
    return "Done"


@shared_task(bind=True)
def translate_to_other_languages(*args, **kwargs):
    obj_id = kwargs.get("obj_id", None)
    current_language = kwargs.get("current_language", None)
    app_label = kwargs.get("app_label", None)
    model = kwargs.get("model", None)
    translation_model = kwargs.get("translation_model", None)

    from django.conf import settings
    from django.contrib.contenttypes.models import ContentType
    from api.utils import google_translate
    TranslationModel = ContentType.objects.get(
        app_label=app_label,
        model=translation_model
    ).model_class()
    ObjModel = ContentType.objects.get(
        app_label=app_label,
        model=model
    ).model_class()
    obj = ObjModel.objects.get(id=obj_id)
    fields = obj.translatable_fields_list
    for language in settings.LANGS:
        code = language["code"]
        if current_language != code:
            translation = TranslationModel.objects.filter(
                master_id=obj.id,
                language_code=code
            )
            if not translation.exists():
                translation = TranslationModel(
                    master_id=obj.id,
                    language_code=code,
                )
            else:
                translation = translation.first()
            for field in fields:
                field_text = google_translate(
                    obj.safe_translation_getter(field, language_code=current_language),
                    current_language,
                    code
                )
                field_text = field_text.capitalize()
                setattr(translation, field, field_text)
            translation.save()