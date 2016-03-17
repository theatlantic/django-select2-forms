from django.contrib.admin import widgets
from django.forms.widgets import CheckboxSelectMultiple, SelectMultiple

from .models.base import SortableThroughModel

class WithSortableThroughTableModelAdminMixin(object):
    def formfield_for_manytomany(self, db_field, request=None, **kwargs):
        """
        Get a form Field for a ManyToManyField.
        """
        # If it uses an intermediary model that isn't auto created and this is
        # not a subclass of SortableThroughModel, don't show
        # a field in admin.

        if not issubclass(db_field.rel.through, SortableThroughModel) \
                and not db_field.rel.through._meta.auto_created:
            return None
        db = kwargs.get('using')

        if db_field.name in self.raw_id_fields:
            kwargs['widget'] = widgets.ManyToManyRawIdWidget(db_field.rel,
                                    self.admin_site, using=db)
            kwargs['help_text'] = ''
        elif db_field.name in (list(self.filter_vertical) + list(self.filter_horizontal)):
            kwargs['widget'] = widgets.FilteredSelectMultiple(
                db_field.verbose_name,
                db_field.name in self.filter_vertical
            )

        if 'queryset' not in kwargs:
            queryset = self.get_field_queryset(db, db_field, request)
            if queryset is not None:
                kwargs['queryset'] = queryset

        form_field = db_field.formfield(**kwargs)
        if isinstance(form_field.widget, SelectMultiple) and not isinstance(form_field.widget, CheckboxSelectMultiple):
            msg = _('Hold down "Control", or "Command" on a Mac, to select more than one.')
            help_text = form_field.help_text
            form_field.help_text = string_concat(help_text, ' ', msg) if help_text else msg
        return form_field
