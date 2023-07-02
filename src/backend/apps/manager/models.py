from typing import Any, Generator
from importlib import import_module
from django.db import models
from django.utils.translation import gettext as _

class Group(models.Model):

    name = models.CharField(
        verbose_name=_("Name"),
        max_length=255,
        blank=False,
        null=False,
        help_text=_('Group identifier')
    )

    def __str__(self) -> str:
        return self.name


class EntryKind(models.Model):
    name = models.CharField(
        verbose_name=_("Name"),
        max_length=255,
        blank=False,
        null=False,
        help_text=_('Kind identifier')
    )

    def __str__(self) -> str:
        return self.name


class Entry(models.Model):
    name = models.CharField(
        verbose_name=_("Name"),
        max_length=255,
        blank=False,
        null=False,
        help_text=_('Entry identifier')
    )
    group = models.ForeignKey(
        to=Group,
        verbose_name=_("Group"),
        blank=False,
        null=False,
        on_delete=models.CASCADE,
        help_text=_('Group folder')
    )
    kind = models.ForeignKey(
        to=EntryKind,
        verbose_name=_("Kind"),
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        help_text=_('Entry kind')
    )
    notes = models.TextField(
        verbose_name=_("Notes"),
        blank=True,
        null=True,
        help_text=_('Aditional notes')
    )

    class Meta:
        verbose_name_plural = _('Entries')

    def __str__(self) -> str:
        return self.name


class FieldKind(models.Model):
    name = models.CharField(
        verbose_name=_("Name"),
        max_length=100,
        blank=False,
        null=False,
        help_text=_('Kind identifier')
    )

    is_secret = models.BooleanField(
        verbose_name=_('Secret'),
        default=False,
        help_text=_(
            'Defines if value must be encrypted and not displayed by default'
        )
    )
    is_required = models.BooleanField(
        verbose_name=_('Required'),
        default=False,
        help_text=_(
            'Defines if at least one element of type is required'
        )
    )

    validators = models.CharField(
        verbose_name=_("Validators"),
        max_length=255,
        blank=True,
        null=True,
        help_text=_('Comma separated values')
    )

    
    def __str__(self) -> str:
        return self.name
    

    def get_validators(self) -> Generator[Any, Any, None]:
        if self.validators:
            for validator in self.validators.split(','):
                mod_name, cls_name = validator.strip().rsplit('.', 1)
                _mod = import_module(mod_name)
                yield getattr(_mod, cls_name)

    
class EntryField(models.Model):
    entry = models.ForeignKey(
        to=Entry,
        verbose_name=_("Entry"),
        blank=False,
        null=False,
        on_delete=models.CASCADE,
        help_text=_('Entry')
    )
    name = models.ForeignKey(
        to=FieldKind,
        verbose_name=_("Name"),
        blank=False,
        null=False,
        on_delete=models.CASCADE,
        help_text=_('Name')
    )
    value = models.CharField(
        verbose_name=_("Value"),
        max_length=255,
        blank=False,
        null=False,
        help_text=_('Field value')
    )

    def __str__(self) -> str:
        return str(self.name)
    
    def get_validators(self) -> Generator[Any, Any, None]:
        yield from self.name.get_validators()

    def save(self, *args, **kwargs) -> None:
        for validator_class in self.get_validators():
            validator_class()(self.value)
        return super().save(*args, **kwargs)
    
    def is_secret(self) -> bool:
        return self.name.is_secret
    is_secret.short_description = _("Is secret")
    is_secret.boolean = True