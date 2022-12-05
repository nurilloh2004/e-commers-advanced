from django.contrib.auth.models import UserManager as BaseUserManager
from parler.managers import TranslatableManager, TranslatableQuerySet
from mptt.managers import TreeManager
from mptt.querysets import TreeQuerySet


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **kwargs):
        user = self.model(
            email=email,
            **kwargs
        )
        user.set_password(password)
        user.is_active = True
        user.save()
        return user


    def create_superuser(self, email, password, **extra_fields):
        user = self.create_user(email, password, **extra_fields)
        user.is_superuser = True
        user.save()
        return user


class CategoryQuerySet(TranslatableQuerySet, TreeQuerySet):
    def as_manager(cls):
        manager = CategoryManager.from_queryset(cls)()
        manager._built_with_as_manager = True
        return manager
    as_manager.queryset_only = True
    as_manager = classmethod(as_manager)


class CategoryManager(TreeManager, TranslatableManager):
    _queryset_class = CategoryQuerySet