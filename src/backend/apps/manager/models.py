from __future__ import annotations
from typing import Any, Dict, Generator
from importlib import import_module
from django.db import models
from django.utils.text import slugify
from django.utils.translation import gettext as _
from yaml import safe_load
from utils.validators import KeywordValidator

class Validator(models.Model):
    name = models.CharField(
        verbose_name=_("Name"),
        max_length=255,
        blank=False,
        null=False,
        help_text=_('Validator identifier')
    )
    validator_class = models.CharField(
        verbose_name=_("Class"),
        max_length=255,
        blank=False,
        null=False,
        help_text=_(
            'Full class import. E.g. "django.core.validators.URLValidator"'
        )
    )

    def __str__(self) -> str:
        return self.name

    
    def get_validator_instance(self) -> Any:
        mod_name, cls_name = self.validator_class.strip().rsplit('.', 1)
        _mod = import_module(mod_name)
        kwargs = {
            arg.key: arg.get_value()
            for arg in self.validator_args.all()
        }
        return getattr(_mod, cls_name)(**kwargs)

    

class ValidatorArgument(models.Model):
    validator = models.ForeignKey(
        to=Validator,
        verbose_name=_("Validator"),
        blank=False,
        null=False,
        on_delete=models.CASCADE,
        related_name='validator_args',
        help_text=_('Validator')
    )
    key = models.CharField(
        verbose_name=_("Name"),
        max_length=255,
        blank=False,
        null=False,
        validators=[KeywordValidator],
        help_text=_('Tag identifier')
    )
    value = models.CharField(
        verbose_name=_("Value"),
        max_length=255,
        blank=False,
        null=False,
        help_text=_('Argument YAML value')
    )


    def __str__(self) -> str:
        return self.key

    
    def get_value(self) -> Any:
        """ Convert string value to python object
        
        Returns:
            Any: Converted value
        """
        if not self.value:
            return self.value

        return safe_load(self.value)
    

    def get_pair_value(self) -> Dict[str, Any]:
        return {self.key: self.get_value()}
    

class Tag(models.Model):
    name = models.CharField(
        verbose_name=_("Name"),
        max_length=255,
        blank=False,
        null=False,
        help_text=_('Tag identifier')
    )
    slug = models.SlugField(blank=True, unique=True)


    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    
    def __str__(self) -> str:
        return self.name


class Group(models.Model):

    name = models.CharField(
        verbose_name=_("Name"),
        max_length=255,
        blank=False,
        null=False,
        help_text=_('Group identifier')
    )

    tags = models.ManyToManyField(
        to=Tag,
        blank=True,
        related_name="groups"
    )

    parent = models.ForeignKey(
        to="self",
        verbose_name=_("Parent"),
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        help_text=_('Parent Group')
    )


    def __str__(self) -> str:
        return self.name
    

    def get_tags_display(self) -> str:
        return ', '.join([t.name for t in self.tags.all()])


class Field(models.Model):
    name = models.CharField(
        verbose_name=_("Name"),
        max_length=100,
        blank=False,
        null=False,
        help_text=_('Field identifier')
    )

    is_secret = models.BooleanField(
        verbose_name=_('Secret'),
        default=False,
        help_text=_(
            'Defines if value must be encrypted and not displayed by default'
        )
    )

    def __str__(self) -> str:
        return self.name


class Template(models.Model):
    name = models.CharField(
        verbose_name=_("Name"),
        max_length=255,
        blank=False,
        null=False,
        help_text=_('Template identifier')
    )


    def __str__(self) -> str:
        return self.name
    

    def get_field_validators(self, field: Field) -> Generator[Any, Any, None]:
        template_field = self.templatefield_set.filter(field=field)
        if template_field:
            yield from template_field[0].get_validators()


class TemplateField(models.Model):

    template = models.ForeignKey(
        to=Template,
        verbose_name=_("Template"),
        blank=False,
        null=False,
        on_delete=models.CASCADE,
        help_text=_('Template')
    )

    field = models.ForeignKey(
        to=Field,
        verbose_name=_("Field"),
        blank=False,
        null=False,
        on_delete=models.CASCADE,
        help_text=_('Field')
    )

    is_required = models.BooleanField(
        verbose_name=_('Required'),
        default=False,
        help_text=_(
            'Defines if at least one element of type is required'
        )
    )

    validators = models.ManyToManyField(
        to=Validator,
        blank=True,
        related_name="template_fields"
    )


    def __str__(self) -> str:
        return str(self.field)
    

    def get_validators(self) -> Generator[Any, Any, None]:
        for validator in self.validators.all():
            yield validator.get_validator_instance()
    

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
    template = models.ForeignKey(
        to=Template,
        verbose_name=_("Template"),
        blank=False,
        null=False,
        on_delete=models.CASCADE,
        help_text=_('Entry template')
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

    
class EntryField(models.Model):
    entry = models.ForeignKey(
        to=Entry,
        verbose_name=_("Entry"),
        blank=False,
        null=False,
        on_delete=models.CASCADE,
        help_text=_('Entry')
    )
    field = models.ForeignKey(
        to=Field,
        verbose_name=_("Field"),
        blank=False,
        null=False,
        on_delete=models.CASCADE,
        help_text=_('Field')
    )
    value = models.CharField(
        verbose_name=_("Value"),
        max_length=255,
        blank=False,
        null=False,
        help_text=_('Field value')
    )


    def __str__(self) -> str:
        return str(self.field)
    

    def get_validators(self) -> Generator[Any, Any, None]:
        yield from self.entry.template.get_field_validators(field=self.field)


    def save(self, *args, **kwargs) -> None:
        for validator in self.get_validators():
            validator(self.value)
        return super().save(*args, **kwargs)
    

    def is_secret(self) -> bool:
        return self.field.is_secret
    is_secret.short_description = _("Is secret")
    is_secret.boolean = True