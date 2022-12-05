from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from parler.models import TranslatableModel, TranslatedFields
from mptt.models import MPTTModel, TreeForeignKey
from rest_framework_simplejwt.tokens import RefreshToken
from django.db.models.signals import post_save
from django.dispatch import receiver

import importlib

from api.data import COUNTRIES_DATA, DEVICE_TYPES
from api.tasks import translate_to_other_languages

utils = importlib.import_module("api.utils")

utils.send_welcome_email("", "", [])

from .managers import CategoryManager, UserManager


class Gender(TranslatableModel):
    class Meta:
        verbose_name = _("Gender")
        verbose_name_plural = _("Genders")

    translations = TranslatedFields(
        title = models.CharField(max_length=50, verbose_name=_("Title"))
    )

    should_translate = models.BooleanField(default=False, verbose_name=_("Translate with google"))

    def __str__(self):
        return self.safe_translation_getter("title", any_language=True)

    def __unicode__(self):
        return self.safe_translation_getter("title", any_language=True)

    @property
    def translatable_fields_list(self):
        return ["title"]

    def save(self, *args, **kwargs):
        if self._state.adding:
            super(Gender, self).save(*args, **kwargs)

        if self.should_translate:
            self.should_translate = False
            current_language = self.get_current_language()
            translate_to_other_languages(
                obj_id=self.id,
                current_language=current_language,
                app_label="api",
                model="gender",
                translation_model="gendertranslation"
            )

        super().save(*args, **kwargs)


class User(AbstractBaseUser, PermissionsMixin):
    class Meta:
        verbose_name = _("User")
        verbose_name_plural = _("Users")

    email = models.CharField(max_length=255, unique=True, verbose_name=_("Email"))
    provider = models.CharField(max_length=255, default="site", verbose_name=_("Registration provider"))
    ref_code = models.CharField(max_length=255, null=True, blank=True, verbose_name=_("Referal code"))

    is_staff = models.BooleanField(default=True)
    is_active = models.BooleanField(default=False)
    is_activater = models.BooleanField(default=False)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = UserManager()

    def save(self, *args, **kwargs):
        if not self.ref_code:
            if not self.id:
                super(User, self).save(*args, **kwargs)
            import hashlib
            _id = str(self.id).encode("utf-8")
            self.ref_code = hashlib.md5(_id).hexdigest()
        super(User, self).save(*args, **kwargs)


    def tokens(self):
        refresh = RefreshToken.for_user(self)
        return {
            "refresh": str(refresh),
            "access": str(refresh.access_token)
        }


#@receiver(post_save, sender=User)
#def update_stock(sender, instance, created, **kwargs):
#    if created and instance.email:
#        try:
#            utils.send_welcome_email("test", "test", [instance.email])
#        except:
#            pass


class OTP(models.Model):
    email = models.CharField(max_length=255, verbose_name=_("Email"))
    code = models.CharField(max_length=20)
    is_activated = models.BooleanField(default=False)
    expires_in = models.DateTimeField()


class Profile(models.Model):
    class Meta:
        verbose_name = _("Profile")
        verbose_name_plural = _("Profiles")

    COUNTRIES = [
        (item[0].lower(), item[1]) for item in COUNTRIES_DATA.items()
    ]
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile", verbose_name=_("User"))
    phone = models.CharField(max_length=20, verbose_name=_("Phone"))
    photo = models.FileField(null=True, blank=True, verbose_name=_("Photo"))
    fullname = models.CharField(max_length=125, default="", verbose_name=_("Fullname"))
    birthday = models.DateField(null=True, blank=True, verbose_name=_("Birthday"))
    gender = models.ForeignKey(Gender, on_delete=models.SET_NULL, null=True, verbose_name=_("Gender"))
    metamask_id = models.TextField(null=True, blank=True, verbose_name=_("Metamask ID"))
    country_code = models.CharField(max_length=255, choices=COUNTRIES, null=True, blank=True, verbose_name=_("Country"))

    @property
    def refs_count(self):
        try:
            return Referal.objects.filter(referencer=self.user).count()
        except Exception as e:
            return 0

    def __str__(self):
        return self.fullname


class Referal(models.Model):
    class Meta:
        verbose_name = _("Referal")
        verbose_name_plural = _("Referals")

    referencer = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="references", verbose_name=_("Referencer"))
    referal = models.OneToOneField(User, on_delete=models.SET_NULL, null=True, related_name="reference", verbose_name=_("Referal"))
    source = models.CharField(max_length=255, null=True, blank=True, verbose_name=_("Source"))

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def ref_code(self):
        try:
            return self.referencer.ref_code
        except:
            return ""


class Category(MPTTModel, TranslatableModel):
    class Meta:
        verbose_name = _("Category")
        verbose_name_plural = _("Categories")

    translations = TranslatedFields(
        title = models.CharField(max_length=50)
    )
    parent = TreeForeignKey("self", on_delete=models.CASCADE, null=True, blank=True, related_name="children", verbose_name=_("Parent category"))

    objects = CategoryManager()

    should_translate = models.BooleanField(default=False, verbose_name=_("Translate with google"))

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.safe_translation_getter("title", any_language=True)

    def __unicode__(self):
        return self.safe_translation_getter("title", any_language=True)

    @property
    def translatable_fields_list(self):
        return ["title"]

    def save(self, *args, **kwargs):
        if self._state.adding:
            super(Category, self).save(*args, **kwargs)

        if self.should_translate:
            self.should_translate = False
            current_language = self.get_current_language()
            translate_to_other_languages(
                obj_id=self.id,
                current_language=current_language,
                app_label="api",
                model="category",
                translation_model="categorytranslation"
            )

        super().save(*args, **kwargs)


class Registerer(models.Model):
    title = models.CharField(max_length=200)


class Entity(TranslatableModel):
    class Meta:
        verbose_name = _("Offer")
        verbose_name_plural = _("Offers")

    registerer = models.ForeignKey(Registerer, on_delete=models.SET_NULL, null=True, blank=True)
    title = models.CharField(max_length=255, verbose_name=_("Title"))

    translations = TranslatedFields(
        title_2 = models.CharField(max_length=255, verbose_name=_("Extra title")),
        description = models.TextField(verbose_name=_("Description"))
    )
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="products", verbose_name=_("Category"))
    photo1 = models.FileField(verbose_name=_("Main photo"))
    photo2 = models.FileField(null=True, blank=True, verbose_name=_("Photo 2"))
    photo3 = models.FileField(null=True, blank=True, verbose_name=_("Photo 3"))
    should_translate = models.BooleanField(default=False, verbose_name=_("Translate with google"))
    sale = models.IntegerField(default=0, verbose_name=_("Sale"), blank=True, null=True)
    partnerka = models.TextField(default=0,verbose_name=_("Partnerka"))
    offer_price = models.IntegerField(default=0,verbose_name="Offer price")
    fake_count = models.IntegerField(default=0, verbose_name=_("Fake count"))

    expires_in = models.DateTimeField()

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        from .utils import smart_truncate
        return self.title or smart_truncate(self.safe_translation_getter("description", any_language=True)) or "-"

    def __unicode__(self):
        from .utils import smart_truncate
        return self.title or smart_truncate(self.safe_translation_getter("description", any_language=True)) or "-"


    @property
    def translatable_fields_list(self):
        return ["title_2", "description"]


    def save(self, *args, **kwargs):
        if self._state.adding:
            super(Entity, self).save(*args, **kwargs)

        if self.should_translate:
            self.should_translate = False
            current_language = self.get_current_language()
            translate_to_other_languages(
                obj_id=self.id,
                current_language=current_language,
                app_label="api",
                model="entity",
                translation_model="entitytranslation"
            )

        super().save(*args, **kwargs)


class ExtraKwargs(models.Model):
    entity = models.ForeignKey(Entity, on_delete=models.CASCADE)
    key = models.CharField(max_length=255)
    value = models.CharField(max_length=255)
#    link = models.URLField(max_length=200,verbose_name="Link",default=0)

    def __str__(self):
        return self.key



class CountryLink(models.Model):
    class Meta:
        verbose_name = _("Country-based link")
        verbose_name_plural = _("Country-based links")

    COUNTRIES = [
        ("all", _("All")),
        *[(country[0].lower(), country[1]) for country in COUNTRIES_DATA.items()]
    ]
    country = models.CharField(max_length=255, choices=COUNTRIES, default="all", verbose_name=_("Country location"))
    link = models.TextField(verbose_name=_("Link"))
    entity = models.ForeignKey(Entity, on_delete=models.CASCADE, related_name="links", verbose_name=_("Offer"))


class View(models.Model):
    class Meta:
        verbose_name = _("View")
        verbose_name_plural = _("Views")

    DEVICES = [
        (device_type, device_type) for device_type in DEVICE_TYPES
    ]
    entity = models.ForeignKey(Entity, on_delete=models.CASCADE, related_name="views", verbose_name=_("Offer"))
    profile = models.ForeignKey(Profile, on_delete=models.SET_NULL, null=True, verbose_name=_("Profile"))
    ip = models.CharField(max_length=20, verbose_name=_("IP address"))
    country = models.CharField(max_length=255, verbose_name=_("Country location"))
    device = models.CharField(max_length=20, choices=DEVICES, verbose_name=_("Device"))
    view1_count = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    def save(self, *args, **kwargs):
        count1 = View.objects.filter(profile=self.profile).count()
        self.view1_count = count1

        super(View, self).save(*args, **kwargs)

class Like(models.Model):
    class Meta:
        verbose_name = _("Like")
        verbose_name_plural = _("Likes")

    DEVICES = [
        (device_type, device_type) for device_type in DEVICE_TYPES
    ]
    entity = models.ForeignKey(Entity, on_delete=models.CASCADE, related_name="likes", verbose_name=_("Offer"))
    profile = models.ForeignKey(Profile, on_delete=models.SET_NULL, null=True, verbose_name=_("Profile"))
    ip = models.CharField(max_length=20, verbose_name=_("IP address"))
    country = models.CharField(max_length=255, verbose_name=_("Country location"))
    device = models.CharField(max_length=20, choices=DEVICES, verbose_name=_("Device"))

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class Partner(TranslatableModel):
    class Meta:
        verbose_name = _("Partner")
        verbose_name_plural = _("Partners")

    translations = TranslatedFields(
        title = models.CharField(max_length=250, null=True, blank=True, verbose_name=_("Title")),
    )
    photo = models.FileField(verbose_name=_("Photo"))

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class SearchTerm(models.Model):
    class Meta:
        verbose_name = _("Search term")
        verbose_name_plural = _("Search terms")

    DEVICES = [
        (device_type, device_type) for device_type in DEVICE_TYPES
    ]
    term = models.CharField(max_length=255, verbose_name=_("Term"))
    profile = models.ForeignKey(Profile, on_delete=models.SET_NULL, null=True, related_name="search_terms", verbose_name=_("Profile"))
    ip = models.CharField(max_length=20, verbose_name=_("IP address"))
    country = models.CharField(max_length=255, verbose_name=_("Country location"))
    device = models.CharField(max_length=20, choices=DEVICES, verbose_name=_("Device"))
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, verbose_name=_("Category"))

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class SubscribeEmail(models.Model):
    class Meta:
        verbose_name = _("Subscribe email")
        verbose_name_plural = _("Subscribe emails")

    DEVICES = [
        (device_type, device_type) for device_type in DEVICE_TYPES
    ]
    email = models.CharField(max_length=255, verbose_name=_("Email"))
    ip = models.CharField(max_length=20, verbose_name=_("IP address"))
    country = models.CharField(max_length=255, verbose_name=_("Country location"))
    device = models.CharField(max_length=20, choices=DEVICES, verbose_name=_("Device"))

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class Banner(models.Model):
    class Meta:
        verbose_name = _("Banner")
        verbose_name_plural = _("Banners")

    COUNTRIES = [
        ("all", _("All")),
        *[(country[0].lower(), country[1]) for country in COUNTRIES_DATA.items()]
    ]
    country = models.CharField(max_length=255, choices=COUNTRIES, default="all", verbose_name=_("Country location"))
    title = models.CharField(max_length=255, verbose_name=_("Title"))
    file = models.FileField(verbose_name=_("File"))
    link = models.TextField(verbose_name=_("Link"))
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, verbose_name=_("Category"))


class BannerClick(models.Model):
    class Meta:
        verbose_name = _("Banner click")
        verbose_name_plural = _("Banner clicks")

    DEVICES = [
        (device_type, device_type) for device_type in DEVICE_TYPES
    ]
    banner = models.ForeignKey(Banner, on_delete=models.CASCADE, related_name="clicks", verbose_name=_("Banner"))
    ip = models.CharField(max_length=20, verbose_name=_("IP address"))
    country = models.CharField(max_length=255, verbose_name=_("Country location"))
    device = models.CharField(max_length=20, choices=DEVICES, verbose_name=_("Device"))
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class StaticTranslation(TranslatableModel):
    class Meta:
        verbose_name = _("Site translation")
        verbose_name_plural = _("Site translations")

    key = models.CharField(max_length=255, verbose_name=_("Key"))

    translations = TranslatedFields(
        value = models.TextField(verbose_name=_("Value"))
    )

    should_translate = models.BooleanField(default=False, verbose_name=_("Translate with google"))

    def __str__(self):
        return self.key

    def __unicode__(self):
        return self.key


    @property
    def translatable_fields_list(self):
        return ["value"]


    def save(self, *args, **kwargs):
        if self._state.adding:
            super(StaticTranslation, self).save(*args, **kwargs)

        if self.should_translate:
            self.should_translate = False
            current_language = self.get_current_language()
            translate_to_other_languages(
                obj_id=self.id,
                current_language=current_language,
                app_label="api",
                model="statictranslation",
                translation_model="statictranslationtranslation"
            )

        super().save(*args, **kwargs)


class ContactLink(TranslatableModel):
    class Meta:
        verbose_name = _("Contact link")
        verbose_name_plural = _("Contact links")

    translations = TranslatedFields(
        title = models.CharField(max_length=50, verbose_name=_("Title"))
    )
    icon = models.FileField(verbose_name=_("Icon"))

    def __str__(self):
        return self.safe_translation_getter("title", any_language=True) or "-"

    def __unicode__(self):
        return self.safe_translation_getter("title", any_language=True) or "-"


class ContactCountryLink(models.Model):
    class Meta:
        verbose_name = _("Country-based contact detail")
        verbose_name_plural = _("Country-based contact details")

    COUNTRIES = [
        ("all", _("All")),
        *[(country[0].lower(), country[1]) for country in COUNTRIES_DATA.items()]
    ]
    country = models.CharField(max_length=255, choices=COUNTRIES, default="all", verbose_name=_("Country location"))
    link = models.TextField(verbose_name=_("Link"))
    contact = models.ForeignKey(ContactLink, on_delete=models.CASCADE, related_name="links", verbose_name=_("Contact"))


class ShareLink(TranslatableModel):
    class Meta:
        verbose_name = _("Share link")
        verbose_name_plural = _("Share links")

    translations = TranslatedFields(
        title = models.CharField(max_length=50, verbose_name=_("Title"))
    )
    slug = models.CharField(max_length=255, null=True, blank=True, verbose_name=_("Slug"))
    icon = models.FileField(verbose_name=_("Icon"))
    prefix_link = models.TextField(verbose_name=_("Prefix link"))

    def __str__(self):
        return self.safe_translation_getter("title", any_language=True) or "-"

    def __unicode__(self):
        return self.safe_translation_getter("title", any_language=True) or "-"


class CryptoContent(TranslatableModel):
    class Meta:
        verbose_name = _("Crypto Content")
        verbose_name_plural = _("Crypto Contents")

    translations = TranslatedFields(
        title1 = models.CharField(_("Title 1"), max_length=255, null=True, blank=True),
        content1 = models.TextField(null=True, blank=True, verbose_name=_("Content 1")),
        title2 = models.CharField(_("Title 2"), max_length=255, null=True, blank=True),
        content2 = models.TextField(null=True, blank=True, verbose_name=_("Content 2"))
    )
    photo1 = models.FileField(null=True, blank=True, verbose_name=_("Photo 1"))
    photo2 = models.FileField(null=True, blank=True, verbose_name=_("Photo 2"))
    should_translate = models.BooleanField(default=True, verbose_name=_("Translate with google"))

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.safe_translation_getter("title1", any_language=True) or "-"

    def __unicode__(self):
        return self.safe_translation_getter("title1", any_language=True) or "-"

    @property
    def translatable_fields_list(self):
        return ["title1", "content1", "title2", "content2"]


    def save(self, *args, **kwargs):
        if self._state.adding:
            super(CryptoContent, self).save(*args, **kwargs)

        if self.should_translate:
            self.should_translate = False
            current_language = self.get_current_language()
            translate_to_other_languages(
                obj_id=self.id,
                current_language=current_language,
                app_label="api",
                model="cryptocontent",
                translation_model="cryptocontenttranslation"
            )

        super().save(*args, **kwargs)


class StaticPage(TranslatableModel):
    class Meta:
        verbose_name = _("Static page")
        verbose_name_plural = _("Static pages")

    translations = TranslatedFields(
        content = models.TextField(null=True, blank=True, verbose_name=_("Content"))
    )
    slug = models.CharField(max_length=255, verbose_name=_("Slug"))

    def __str__(self):
        return self.slug or "-"

    def __unicode__(self):
        return self.slug or "-"


class TemplateMessage(models.Model):
    message = models.TextField()
    def __str__(self):
        return self.message
    class Meta:
        verbose_name = _("Template Message")
        verbose_name_plural = _("Template Messages")

class Notification(models.Model):
    user = models.ManyToManyField(User)
    template = models.ForeignKey(TemplateMessage, on_delete = models.SET_NULL, null=True, blank=True)
    message = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.created_at)
    class Meta:
        verbose_name = _("Notification")
        verbose_name_plural = _("Notifications")


class Order(models.Model):
    STATUS_CHOICES = (
        ('Sotib olingan', 'Sotib olingan'),
        ('Sotib olinmagan', 'Sotib olinmagan'),
    )
    user = models.ForeignKey(Profile, on_delete=models.CASCADE)
    order_item = models.ForeignKey(Entity, on_delete=models.CASCADE)
    status = models.CharField(max_length=255, choices=STATUS_CHOICES)
    order_date = models.DateTimeField(auto_now_add=True)


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    product = models.ForeignKey(Entity, on_delete=models.CASCADE)
    total_price = models.PositiveIntegerField()
    quantity = models.IntegerField(default=1)