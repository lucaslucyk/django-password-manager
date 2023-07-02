from typing import Any
from xml.dom import ValidationErr
from django.contrib import admin
from apps.manager import models
# Register your models here.


class ItemsInline(admin.TabularInline):
    model = models.EntryField
    extra = 0
    ordering = ('name',)
    fields = ('name', 'value', 'is_secret', )
    readonly_fields = ('is_secret', )


@admin.register(models.Entry)
class EntryAdmin(admin.ModelAdmin):
    inlines = [ItemsInline]
    model = models.Entry
    fields = ('name', 'group', 'kind', 'notes')


admin.site.register(models.Group)
admin.site.register(models.EntryKind)
admin.site.register(models.EntryField)
admin.site.register(models.FieldKind)