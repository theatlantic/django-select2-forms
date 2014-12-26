# django-select2-forms

**django-select2-forms** is a project that makes available Django form fields
that use the [Select2 javascript plugin](http://ivaynberg.github.com/select2/).
It was created by developers at [The Atlantic](http://www.theatlantic.com/).  I
have (manually) merged in some of the changes from
[RadiantFlow](http://www.github.com/radiantflow/django-select2-forms/).  The
main differences from TheAtlantic's version is that this supports Django 1.7 and Python 3.

* [Installation](#installation)
* [Configuration](#configuration)
* [Settings](#settings)
* [Usage](#usage)
   * [select2.fields.ForeignKey examples](#select2fieldsforeignkey-examples)
   * [select2.fields.ManyToManyField examples](#select2fieldsmanyomanyfield-examples)
   * [form field example](#form-field-example)
* [API Documentation](#api-documentation)
* [License](#license)


## Installation

The recommended way to install is with pip:

    pip install -e git+git://github.com/JP-Ellis/django-select2-forms.git#egg=django-select2-forms

If the source is already checked out, use setuptools:

    python setup.py install


## Configuration

`django-select2-forms` serves static assets using
[django.contrib.staticfiles](https://docs.djangoproject.com/en/1.5/howto/static-files/),
and so requires that `"select2"` be added to your settings' `INSTALLED_APPS`:

```python
INSTALLED_APPS = (
    # ...
    'select2',
)
```

You will also need to add the following inside your Django template header:

```html
{% load select2 %}
<!-- ... -->
<head>
    <!-- Your other CSS files -->
    {% select2_css %}

    <!-- YOur other JS files -->
    {% select2_javascript %}
</head>
```

This plugin relies of the Select2 JavaScript library which itself depends on
jQuery.  By default `{% select2_javascript %}` will **not** include these
libraries, but these can be included by adding the following to your settings:

```python
SELECT2 = {
  'include_jquery': True,
  'include_select2': True
}
```

To use django-select2-forms' ajax support, `'select2.urls'` must be included in
your urls.py `urlpatterns`:

```python
urlpatterns = patterns('',
    # ...
    url(r'^select2/', include('select2.urls')),
)
```


## Settings

Plugin settings can be set by adding `SELECT2` dictionary within the
settings.

| Key               | Default   | Description                                                                                                       |
| ----------------- | --------- | ----------------------------------------------------------------------------------------------------------------- |
| `jquery_url`      | See below | The URL to the jQuery library JS.                                                                                 |
| `select2_url`     | See below | The base URL to the Select2 library.                                                                              |
| `select2_css_url` | `None`    | The full URL to the Select2 CSS.  If `None`, it will default to `select2_url + 'select2.min.css'`.                |
| `select2_js_url`  | `None`    | The full URL to the Select2 JS.  If `None`, it will default to `select2_url + 'select2.min.js'`.                  |
| `theme_url`       | `None`    | The full URL to a Select2 CSS theme.                                                                              |
| `include_jquery`  | `False`   | Whether jQuery is automatically included.  If `False`, then jQuery will have to be included manually.             |
| `include_select2` | `False`   | Whether the Select2 library is automatically included.  If `False`, the jQuery will have to be included manually. |

The `jquery_url` default is `//code.jquery.com/jquery.min.js`.  The
`select2_url` default is `//cdnjs.cloudflare.com/ajax/libs/select2/3.5.2/`.


## Usage

The simplest way to use `django-select2-forms` is to use
`select2.fields.ForeignKey` and `select2.fields.ManyToManyField` in place of
`django.db.models.ForeignKey` and `django.db.models.ManyToManyField`,
respectively. These fields extend their Django equivalents and take the same
arguments, along with extra optional keyword arguments.

The replacement can be done in existing models which had
`django.db.models.ForeignKey` and `django.db.models.ManyToManyField`.

### select2.fields.ForeignKey examples

In the following two examples, an "entry" is associated with only one author.
The example below does not use ajax, but instead performs autocomplete
filtering on the client-side using the `<option>` elements (the labels of which
    are drawn from `Author.__str__()`) in an html `<select>`.

```python
class Author(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Entry(models.Model):
    author = select2.fields.ForeignKey(Author,
        overlay="Choose an author...")
```

This more advanced example autocompletes via ajax using the `Author.name` field
and limits the autocomplete search to `Author.objects.filter(active=True)`

```python
class Author(models.Model):
    name = models.CharField(max_length=100)
    active = models.BooleanField()

class Entry(models.Model):
    author = select2.fields.ForeignKey(Author,
        limit_choices_to=models.Q(active=True),
        ajax=True,
        search_field='name',
        overlay="Choose an author...",
        js_options={
            'quiet_millis': 200,
        })
```

### select2.fields.ManyToManyField examples

In the following basic example, entries can have more than one author. This
example does not do author name lookup via ajax, but populates `<option>`
elements in a `<select>` with `Author.__str__()` for labels.

```python
class Author(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Entry(models.Model):
    authors = select2.fields.ManyToManyField(Author)
```

The following "kitchen sink" example allows authors to be ordered, and uses
AJAX to auto-complete on two variants of an author's name.

```python
from django.db import models
from django.db.models import Q
import select2.fields
import select2.models

class Author(models.Model):
    name = models.CharField(max_length=100)
    alt_name = models.CharField(max_length=100, blank=True, null=True)

class EntryAuthors(select2.models.SortableThroughModel):
    """
    A custom m2m through table, with a `position` field for sorting.

    This allows us to store and retrieve an ordered list of authors for an entry.
    """
    entry = models.ForeignKey('Entry')
    author = models.ForeignKey(Author)
    position = models.PositiveSmallIntegerField()

class Entry(models.Model):
    categories = select2.fields.ManyToManyField(Author,
        through='EntryAuthors',
        ajax=True,
        search_field=lambda q: Q(name__icontains=q) | Q(alt_name__icontains=q),
        sort_field='position',
        js_options={'quiet_millis': 200})
```

### form field example

If you don't need to use the ajax features of `django-select2-forms` it is
possible to use select2 on django forms without modifying your models. The
select2 formfields exist in the `select2.fields` module and have the same class
names as their standard django counterparts (`ChoiceField`,
    `MultipleChoiceField`, `ModelChoiceField`, `ModelMultipleChoiceField`).
Here is the first `ForeignKey` example above, done with django formfields.

```python
class AuthorManager(models.Manager):
    def as_choices(self):
        for author in self.all():
            yield (author.pk, unicode(author))


class Author(models.Model):
    name = models.CharField(max_length=100)
    objects = AuthorManager()

    def __str__(self):
        return self.name


class Entry(models.Model):
    author = models.ForeignKey(Author)


class EntryForm(forms.ModelForm):
    author = select2.fields.ChoiceField(
            choices=Author.objects.as_choices(),
            overlay="Choose an author...")

    class Meta:
        model = Entry
```


## API Documentation

All fields take the arguments as their corresponding Django version.  In addition, the following keyword arguments are available.

### class select2.fields.ForeignKey(to, kwargs)

`select2.fields.ForeignKey` takes the following keywords arguments:

| Key              | Default | Description                                                                                                                                                                                                              |
| --- | --- | --- |
| `overlay`        |         | The placeholder text that will be displayed in an empty Select2 field.                                                                                                                                                   |
| `ajax`           | `False` | If `True`, the Select2 options will be populated using AJAX.  For this to work, the `select2.urls` must be added to your URL mappings.                                                                                   |
| `search_field`   | `None`  | The field name on the related model that will be searched.  This can also be a function which takes a search string as the argument and returns a `django.db.models.Q` object.  This field is required is `ajax = True`. |
| `case_sensitive` | `False` | Whether the search defined by `search_field` above should be case sensitive.  If `search_field` is a `django.db.models.Q`, this argument does nothing.                                                                   |
| `js_options`     | `{}`    | A dictionary that is passed as options to `jQuery.fn.select2()` in JavaScript.                                                                                                                                           |

### class select2.fields.ManyToManyField(to, kwargs)

`select2.fields.ManyToManyField` takes all the same arguments as `select2.fields.ForeignKey`. It takes the following keyword arguments in addition.

| Key          | Default | Description                                                                                                                                                                 |
| ------------ | ------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `sort_field` |         | The field name on the `select2.models.SortableThroughModel` class to use when storing sort position on save.  See the "kitchen sink" example above to see how this is used. |


## License

The django code is licensed under the
[Simplified BSD License](http://opensource.org/licenses/BSD-2-Clause) and
is copyright The Atlantic Media Company. View the `LICENSE` file under the
root directory for complete license and copyright information.

The Select2 javascript library included is licensed under the
[Apache Software Foundation License Version 2.0](http://www.apache.org/licenses/LICENSE-2.0).
View the file `select2/static/select2/select2/LICENSE` for complete license
and copyright information about the Select2 javascript library.
