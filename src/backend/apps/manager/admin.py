from pipes import Template
from typing import Any
from xml.dom import ValidationErr
from django.contrib import admin
from apps.manager import models

from .forms import EntryFieldForm


class ValidatorArgumentInline(admin.TabularInline):
    model = models.ValidatorArgument
    extra = 0
    ordering = ('key', )
    fields = ('key', 'value')

@admin.register(models.Validator)
class ValidatorAdmin(admin.ModelAdmin):
    inlines = [ValidatorArgumentInline]
    model = models.Validator
    fields = ('name', 'validator_class')
    search_fields = ('name', )
    list_display = ('name', 'validator_class')


class TemplateFieldInline(admin.TabularInline):
    model = models.TemplateField
    extra = 0
    ordering = ('field', )
    fields = ('field', 'is_required', 'validators')
    autocomplete_fields = ('field', 'validators', )

@admin.register(models.Template)
class TemplateAdmin(admin.ModelAdmin):
    inlines = [TemplateFieldInline]
    model = models.Template
    fields = ('name', )
    search_fields = ('name', )


class EntryFieldInline(admin.TabularInline):
    model = models.EntryField
    extra = 0
    form = EntryFieldForm
    autocomplete_fields = ("field", )
    readonly_fields = ('is_secret', )


@admin.register(models.Entry)
class EntryAdmin(admin.ModelAdmin):
    inlines = [EntryFieldInline]
    model = models.Entry
    fields = ('name', 'group', 'template', 'notes')
    autocomplete_fields = ("group", "template")
    list_display = ('name', 'group', 'template')


@admin.register(models.Tag)
class TagAdmin(admin.ModelAdmin):
    model = models.Tag
    fields = ('name', 'slug')
    readonly_fields = ('slug', )
    ordering = ('name', )
    search_fields = ('name', )
    list_display = ('name', 'slug')
    

@admin.register(models.Group)
class GroupAdmin(admin.ModelAdmin):
    model = models.Group
    fields = ('name', 'tags', 'parent')
    ordering = ('name', )
    search_fields = ('name', 'parent')
    autocomplete_fields = ('tags', 'parent')
    list_display = ('name', 'get_tags_display', 'parent')


@admin.register(models.Field)
class FieldAdmin(admin.ModelAdmin):
    model = models.Field
    fields = ('name', 'is_secret')
    ordering = ('name', )
    search_fields = ('name', )
    list_display = ('name', 'is_secret')