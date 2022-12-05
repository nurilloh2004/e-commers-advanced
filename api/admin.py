from django.contrib import admin
from django.forms import forms
from parler.admin import TranslatableAdmin
from parler.forms import TranslatableModelForm
from mptt.admin import MPTTModelAdmin
from mptt.forms import MPTTAdminForm
from django import forms
from django.contrib.auth.models import Group
from django.utils.translation import gettext_lazy as _
from django.utils.html import format_html
from django.contrib.auth import get_user_model
from django.contrib.admin.widgets import FilteredSelectMultiple
from django_summernote.admin import SummernoteModelAdmin
from django_celery_results.models import GroupResult, TaskResult
from django_summernote.models import Attachment

from api.models import Category,Partner,  Gender,CountryLink,ExtraKwargs, Profile,User,ContactCountryLink, Order, Like, View,SearchTerm, Entity ,Banner,TemplateMessage, Notification, SubscribeEmail,StaticTranslation,ContactLink,ShareLink,CryptoContent,Referal,StaticPage
from api.mixins import *
from api import models
User = get_user_model()

admin.site.register(Order)
class UserAdmin(
        admin.ModelAdmin,
        SuperUserEditableFieldsMixin,
        AdminUserCannotDeleteMixin
    ):
    # fields = ["id", "email", "ref_code", "is_staff", "is_active"]
    list_display = ["id", "email", "ref_code", "is_staff", "is_active"]
    list_display_links = ["id", "email"]
    search_fields = ["id", "email"]
    list_filter = ["id", "email"]
    readonly_fields = ["id", "last_login", "ref_code", "password"]


class ProfileAdmin(
        admin.ModelAdmin,
        SuperUserEditableFieldsMixin,
        AdminUserCannotDeleteMixin
    ):
    list_display = ["id", "fullname", "phone", "get_ref_code", "get_ref_count", "get_metamask_id", "gender"]
    list_display_links = ["id", "fullname", "phone"]
    search_fields = ["id", "fullname", "phone", "user__ref_code"]
    list_filter = ["id", "fullname", "phone", "user__ref_code", "country_code"]
    readonly_fields = ["id", "user", "gender"]

    def get_urls(self):
        from django.urls import path
        from api.func_views import email_list_file_view
        urls = super(ProfileAdmin, self).get_urls()
        my_urls = [
            path("email-list-file/", email_list_file_view)
        ]
        return my_urls + urls


    def get_metamask_id(self, obj=None):
        try:
            return (obj.metamask_id)[:15] + "..."
        except:
            return ""
    get_metamask_id.short_description = _("Metamask ID")

    def get_ref_code(self, obj=None):
        try:
            return obj.user.ref_code
        except:
            return ""
    get_ref_code.short_description = _("Referal code")

    def get_ref_count(self, obj=None):
        return obj.refs_count
    get_ref_count.short_description = _("Referal count")


class ReferalAdmin(
        admin.ModelAdmin,
        SuperUserEditableFieldsMixin,
        AdminUserCannotDeleteMixin
    ):
    list_display = ["id", "referencer", "referal", "source", "ref_code", "created_at", "updated_at"]
    search_fields = ["id", "referencer__profile__phone", "referencer__email", "referencer__ref_code", "referencer__profile__fullname", "referal__profile__phone", "referal__profile__fullname", "referal__email"]
    list_filter = ["id", "referencer", "referal", "source"]
    readonly_fields = ["id", "referencer", "referal", "source", "created_at", "updated_at"]


class EmailAdmin(
        admin.ModelAdmin,
        SuperUserEditableFieldsMixin,
        AdminUserCannotDeleteMixin
    ):
    list_display = ["id", "email", "device", "country", "ip"]
    list_display_links = ["id", "email"]
    search_fields = ["id", "email", "device", "country", "ip"]
    list_filter = ["email", "device", "country"]
    readonly_fields = ["id", "email", "device", "country", "ip"]


class SearchTermAdmin(admin.ModelAdmin):
    list_display = ["id", "term", "profile", "device", "country", "ip", "category"]
    list_display_links = ["id", "term", "profile", "category"]
    search_fields = ["id", "term", "device", "country", "ip", "category__translations__title"]
    list_filter = ["id", "term", "profile", "device", "country", "ip", "category"]
    readonly_fields = ["id", "term", "profile", "device", "country", "ip", "category"]


class CategoryAdminForm(MPTTAdminForm, TranslatableModelForm):
    pass


class CategoryAdmin(TranslatableAdmin, MPTTModelAdmin):
    form = CategoryAdminForm
    list_display = ["id", "title", "entity_count"]
    list_display_links = ["id", "title"]
    search_fields = ["id", "translations__title"]
    list_filter = ["id", "translations__title"]

    def entity_count(self, obj=None):
        try:
            return Entity.objects.filter(category=obj).count()
        except:
            return 0
    entity_count.short_description = _("Entity count")


class CryptoContentAdmin(TranslatableAdmin):
    pass



class CountryLinkAdmin(admin.StackedInline):
    class CountryLinkForm(forms.ModelForm):
        link = forms.CharField(widget=forms.TextInput(attrs={"style": "width: 500px;"}))

        class Meta:
            model = CountryLink
            fields = "__all__"
    model = CountryLink
    form = CountryLinkForm


class ExtraKwargsAdmin(admin.StackedInline):
    model = ExtraKwargs
    extra = 1


class EntityAdmin(TranslatableAdmin):
    inlines = [CountryLinkAdmin]
    list_display = ["id", "title", "get_description", "get_views", "get_likes", "category"]
    list_display_links = ["id", "title", "get_description", "category"]
    search_fields = ["id", "translations__title", "translations__description"]
    list_filter = ["category", "links__country","partnerka"]
    inlines = [ExtraKwargsAdmin, CountryLinkAdmin]

    def get_description(self, obj=None):
        try:
            if len(obj.description) > 50:
                return "{}...".format(obj.description[:50])
            else:
                return obj.description
        except:
            return ""
    get_description.short_description = _("Description")

    def get_views(self, obj=None):
        return View.objects.filter(entity=obj).count()
    get_views.short_description = _("Views")

    def get_likes(self, obj=None):
        return Like.objects.filter(entity=obj).count()
    get_likes.short_description = _("Likes")


class ViewAdmin(admin.ModelAdmin):
    list_display = ["id", "entity", "profile", "device", "country", "ip","get_view_count"]
    list_display_links = ["id", "entity", "profile"]
    readonly_fields = ["id", "entity", "profile", "device", "country", "ip","view1_count"]

    def get_view_count(self, obj):
        return View.objects.filter(profile=obj.profile).count()


class LikeAdmin(admin.ModelAdmin):
    list_display = ["id", "entity", "profile", "device", "country", "ip"]
    list_display_links = ["id", "entity", "profile"]
    readonly_fields = ["id", "entity", "profile", "device", "country", "ip"]


class BannerAdmin(admin.ModelAdmin):
    list_display = ["id", "title", "category", "link", "country"]
    list_display_links = ["id", "title", "link"]
    search_fields = ["id", "title", "link", "country"]
    list_filter = ["id", "title", "category", "link", "country"]


class StaticTranslationAdmin(TranslatableAdmin):
    list_display = ["id", "key", "value"]
    list_display_links = ["key"]
    search_fields = ["key"]


class ShareLinkAdmin(TranslatableAdmin):
    list_display = ["id", "prefix_link"]

    def get_prepopulated_fields(self, request, obj=None):
        return {
            "slug": ("title",)
        }


class ContactCountryLinkForm(forms.ModelForm):
    link = forms.CharField(widget=forms.TextInput(attrs={"style": "width: 500px;"}))

    class Meta:
        model = ContactCountryLink
        fields = "__all__"


class ContactCountryLinkAdmin(admin.StackedInline):
    model = ContactCountryLink
    form = ContactCountryLinkForm


class ContactLinkAdmin(TranslatableAdmin):
    list_display = ["id", "title", "get_icon"]
    list_display_links = ["id", "title", "get_icon"]
    search_fields = ["id", "translations__title"]
    list_filter = ["id", "translations__title"]
    inlines = [ContactCountryLinkAdmin]

    def get_icon(self, obj=None):
        try:
            return format_html("<img src='{}' style='width: 30px; height: 30px; object-fit: cover; object-position: center;'/>".format(obj.icon.url))
        except:
            return ""
    get_icon.short_description = _("Icon")


class StaticPageAdmin(TranslatableAdmin, SummernoteModelAdmin):
    summernote_fields = ("content",)


class GroupAdminForm(forms.ModelForm):
    class Meta:
        model = Group
        exclude = []

    users = forms.ModelMultipleChoiceField(
         queryset=User.objects.all(),
         required=False,
         widget=FilteredSelectMultiple('users', False)
    )

    def __init__(self, *args, **kwargs):
        super(GroupAdminForm, self).__init__(*args, **kwargs)
        if self.instance.pk:
            self.fields['users'].initial = self.instance.user_set.all()

    def save_m2m(self):
        self.instance.user_set.set(self.cleaned_data['users'])

    def save(self, *args, **kwargs):
        instance = super(GroupAdminForm, self).save()
        self.save_m2m()
        return instance


admin.site.unregister(Group)

class GroupAdmin(admin.ModelAdmin):
    form = GroupAdminForm
    filter_horizontal = ['permissions']


class TemplateMessageAdmin(admin.ModelAdmin):
    pass

#@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('template', 'message')
class PartnerAdmin(TranslatableAdmin):
    list_display = ('title', 'photo')
admin.site.register(Group, GroupAdmin)
admin.site.register(Partner,PartnerAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Gender, TranslatableAdmin)
admin.site.register(Profile, ProfileAdmin)
admin.site.register(User, UserAdmin)
admin.site.register(SearchTerm, SearchTermAdmin)
admin.site.register(Entity, EntityAdmin)
admin.site.register(View, ViewAdmin)
admin.site.register(Like, LikeAdmin)
admin.site.register(Banner, BannerAdmin)
admin.site.register(TemplateMessage, TemplateMessageAdmin)
admin.site.register(Notification, NotificationAdmin)
admin.site.register(SubscribeEmail, EmailAdmin)
admin.site.register(StaticTranslation, StaticTranslationAdmin)
admin.site.register(ContactLink, ContactLinkAdmin)
admin.site.register(ShareLink, ShareLinkAdmin)
admin.site.register(CryptoContent, CryptoContentAdmin)
admin.site.register(Referal, ReferalAdmin)
admin.site.register(StaticPage, StaticPageAdmin)

admin.site.unregister(GroupResult)
admin.site.unregister(TaskResult)
admin.site.unregister(Attachment)


