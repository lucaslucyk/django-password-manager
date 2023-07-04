from django import forms
from django.core.exceptions import ValidationError
from .models import EntryField
from django.utils.translation import gettext_lazy as _


class EntryFieldForm(forms.ModelForm):
    class Meta:
        model = EntryField
        fields = ('field', 'value')
        readonly_fields = ('is_secret', )
        ordering = ('field__name')


    def clean(self):
        cleaned_data = super().clean()
        entry = cleaned_data.get('entry')
        value = cleaned_data.get('value')
        field = cleaned_data.get('field')
        for validator in entry.template.get_field_validators(field=field):
            try:
                validator(value)
            except ValidationError as err:
                errors = ', '.join(err)
                self.add_error('value', f"{_('Validation failure')}: {errors}")
        return cleaned_data
