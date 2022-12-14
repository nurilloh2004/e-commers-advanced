from rest_framework import serializers
from parler_rest.serializers import TranslatableModelSerializer, TranslatedFieldsField
from rest_framework_recursive.fields import RecursiveField
from django.db import transaction
from django.utils.translation import gettext_lazy as _

from api.mixins import TranslatedSerializerMixin
from api.models import *
from api.utils import check_and_save_referal, get_obj_link_for_country


class CategorySerializer(
        TranslatedSerializerMixin,
        TranslatableModelSerializer
    ):
    translations = TranslatedFieldsField(shared_model=Category)
    children = RecursiveField(many=True)

    class Meta:
        model = Category
        fields = ["id", "translations", "children"]


class CategoryItemSerializer(
        TranslatedSerializerMixin,
        TranslatableModelSerializer
    ):
    translations = TranslatedFieldsField(shared_model=Category)

    class Meta:
        model = Category
        fields = ["id", "translations"]


class UserSerializer(serializers.ModelSerializer):
    ref = serializers.CharField(write_only=True)
    source = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ["id", "email", "password", "ref_code", "ref", "source"]
        extra_kwargs = {
            "password": {
                "write_only": True
            },
            "ref_code": {
                "required": False
            },
            "ref": {
                "required": False
            },
            "source": {
                "required": False
            }
        }


class GenderSerializer(
        TranslatedSerializerMixin,
        TranslatableModelSerializer
    ):
    translations = TranslatedFieldsField(shared_model=Gender)

    class Meta:
        model = Gender
        fields = ["id", "translations"]


class ProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(many=False)
    total_refs = serializers.SerializerMethodField()
    gender_text = serializers.SerializerMethodField()
    email = serializers.SerializerMethodField()
    class Meta:
        model = Profile
        fields = ["id", "phone", "fullname","email", "photo", "birthday", "metamask_id", "user", "gender", "gender_text", "total_refs"]
        extra_kwargs = {
            "phone": {
                "required": False
            }
        }

    def create(self, validated_data):
        user_data = validated_data.pop("user")
        with transaction.atomic():
            user = User(email=user_data["email"])
            user.set_password(user_data["password"])
            user.save()
            check_and_save_referal(user, user_data)
            profile = Profile(**validated_data, user=user)
            profile.save()
        return profile


    def get_total_refs(self, obj):
        try:
            return obj.refs_count
        except:
            return 0
    def get_email(self, obj):
        try:
            return obj.email
        except:
            return None
    def get_gender_text(self, obj):
        try:
            return obj.gender.title
        except:
            return _("male")



class EntityDetailSerializer(
        TranslatedSerializerMixin,
        TranslatableModelSerializer
    ):
    class Meta:
        model = Entity
        fields = ("id", "title", "translations", "category", "photo1", "photo2", "photo3","should_translate", "sale", "offer_price", "fake_count", "expires_in", "translatable_fields_list")



class EntitySerializer(
        TranslatedSerializerMixin,
        TranslatableModelSerializer
    ):
    translations = TranslatedFieldsField(shared_model=Entity)
    photos = serializers.SerializerMethodField()
    link = serializers.SerializerMethodField()
    category = CategoryItemSerializer(many=False)
    like = serializers.SerializerMethodField()
    views = serializers.SerializerMethodField()
    registerer = serializers.SerializerMethodField()
    sale = serializers.SerializerMethodField()
    class Meta:
        model = Category
        fields = ["id", "category", "like", "translations", "title", "photos", "link", "views", "registerer", "sale"]

    def get_sale(self,obj):
        if obj.sale:
            return obj.sale

    def get_photos(self, obj):
        result = []
        if obj.photo1:
            result.append(obj.photo1.url)
        if obj.photo2:
            result.append(obj.photo2.url)
        if obj.photo3:
            result.append(obj.photo3.url)
        return result

    def get_link(self, obj):
        country = self.context.get("country", None)
        return get_obj_link_for_country(obj, country)

    def get_like(self, obj):
        try:
            like_obj = Like.objects.filter(
                entity=obj,
                profile=self.context.get("request", None).user.profile
            )
            if like_obj.exists():
                return {
                    "id": like_obj.first().id
                }
        except:
            pass
        return None

    def get_views(self, obj):
        return View.objects.filter(entity=obj).count() + obj.fake_count

    def get_registerer(self, obj):
        if obj.registerer:
            return obj.registerer.title
        return None

 #   def get_sale(self, obj):
 #	if obj.sale:
 #	    return obj.sale
 #	else:
 #           return obj
class PartnerSerializer(
        TranslatedSerializerMixin,
        TranslatableModelSerializer
    ):
    translations = TranslatedFieldsField(shared_model=Partner)

    class Meta:
        model = Partner
        fields = ["id", "translations", "photo"]


class SearchTermSerializer(serializers.ModelSerializer):
    class Meta:
        model = SearchTerm
        fields = ["id", "term"]


class ViewSerializer(serializers.ModelSerializer):
    class Meta:
        model = View
        fields = ["id", "entity"]


class BannerClickSerializer(serializers.ModelSerializer):
    class Meta:
        model = BannerClick
        fields = ["id", "banner"]


class LikeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Like
        fields = ["id", "entity"]


class SubscribeEmailSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubscribeEmail
        fields = ["id", "email"]


class BannerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Banner
        fields = ["id", "title", "file", "link"]


class CountrySerializer(serializers.ModelSerializer):
    class Meta:
        model = CountryLink
        fields = ["id"]


class StaticTranslationSerializer(
        TranslatableModelSerializer
    ):
    translations = TranslatedFieldsField(shared_model=StaticTranslation)

    class Meta:
        model = StaticTranslation
        fields = ["id", "key", "translations"]

    def to_representation(self, instance):
        from django.conf import settings
        from api.utils import get_lang
        inst_rep = super().to_representation(instance)
        request = self.context.get("request", None) or self.request
        lang_code = self.context.get("lang", None)
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


class ContactLinkSerializer(
        TranslatedSerializerMixin,
        TranslatableModelSerializer
    ):
    translations = TranslatedFieldsField(shared_model=ContactLink)
    link = serializers.SerializerMethodField()

    class Meta:
        model = ContactLink
        fields = ["id", "translations", "icon", "link"]

    def get_link(self, obj):
        country = self.context.get("country", None)
        print("link country", country)
        return get_obj_link_for_country(obj, country)


class ShareLinkSerializer(
        TranslatedSerializerMixin,
        TranslatableModelSerializer
    ):
    translations = TranslatedFieldsField(shared_model=ShareLink)

    class Meta:
        model = ShareLink
        fields = ["id", "translations", "icon", "prefix_link"]


class CryptoContentSerializer(
        TranslatedSerializerMixin,
        TranslatableModelSerializer
    ):
    translations = TranslatedFieldsField(shared_model=CryptoContent)

    class Meta:
        model = CryptoContent
        fields = ["id", "translations", "photo1", "photo2"]


class StaticPageSerializer(
        TranslatedSerializerMixin,
        TranslatableModelSerializer
    ):
    translations = TranslatedFieldsField(shared_model=StaticPage)

    class Meta:
        model = StaticPage
        fields = ["id", "translations", "slug"]


class OrderSerializer(serializers.ModelSerializer):
    """Serializer for Order."""
    order_item = EntitySerializer(many=True)
    user = ProfileSerializer(many=True)


    class Meta:
        model = Order
        fields = ['id', 'user', 'order_item', 'status', 'order_date']
        read_only_fields = ['id']

    def _get_or_create_order_item(self, order_item, order):
        """Handle getting or creating order item as needed."""
        auth_user = self.context['request'].user
        for order in order_item:
            order_obj, created = Entity.objects.get_or_create(
                user=auth_user,
                **order,

            )

            order.order_item.add(order_obj)

    def _get_or_create_user(self, user, order):
        pass

    def update(self, instance, validated_data):
        """Update recipe."""
        order_item = validated_data.pop('order_item', None)
        user = validated_data.pop('user', None)
        if order_item is not None:
            instance.order_item.clear()
            self._get_or_create_order_item(order_item, instance)
        if user is not None:
            instance.user.clear()
            self._get_or_create_user(user, instance)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()
        return instance