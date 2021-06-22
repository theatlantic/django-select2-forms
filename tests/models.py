from django.db import models
from django.db.models import Q

from select2.fields import (
    ForeignKey as Select2ForeignKey, ManyToManyField as Select2ManyToManyField)


class Publisher(models.Model):
    name = models.CharField(max_length=100)
    country = models.CharField(max_length=2)

    class Meta:
        ordering = ('name',)

    def __str__(self):
        return self.name


class Author(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    alive = models.BooleanField(default=True)

    class Meta:
        ordering = ('first_name', 'last_name')

    def __str__(self):
        return "%s %s" % (self.first_name, self.last_name)


class Library(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Book(models.Model):
    title = models.CharField(max_length=100)
    library = models.ForeignKey(Library, blank=True, null=True, on_delete=models.CASCADE)

    publisher = Select2ForeignKey(
        Publisher, blank=True, null=True, related_name="+",
        overlay="Choose a publisher...", on_delete=models.CASCADE)

    us_publisher = Select2ForeignKey(
        Publisher, blank=True, null=True, related_name="+",
        verbose_name="U.S. Publisher", limit_choices_to=Q(country='US'),
        on_delete=models.CASCADE)

    publisher_ajax = Select2ForeignKey(
        Publisher, blank=True, null=True, related_name="+",
        verbose_name="Publisher (AJAX)", ajax=True, search_field='name',
        on_delete=models.CASCADE)

    us_publisher_ajax = Select2ForeignKey(
        Publisher, blank=True, null=True, related_name="+",
        verbose_name="U.S. Publisher (AJAX)", ajax=True, search_field='name',
        limit_choices_to=Q(country='US'), on_delete=models.CASCADE)

    authors_kwargs = {
        'blank': True,
        'sort_field': 'position',
    }

    authors = Select2ManyToManyField(Author, overlay="Choose authors...", **authors_kwargs)

    alive_authors = Select2ManyToManyField(
        Author, limit_choices_to=Q(alive=True), db_table="tests_book_alive_authors",
        related_name="book_set1", **authors_kwargs)
    authors_ajax = Select2ManyToManyField(
        Author, verbose_name="Authors (AJAX)", ajax=True, search_field="last_name",
         db_table="tests_book_authors_ajax", related_name="book_set2",
         **authors_kwargs)
    alive_authors_ajax = Select2ManyToManyField(
        Author, verbose_name="Alive authors (AJAX)", ajax=True, search_field="last_name",
        limit_choices_to=Q(alive=True), related_name="book_set3",
        db_table="tests_book_alive_authors_ajax", **authors_kwargs)

    # For testing search_field passed a callable
    authors_full_name_ajax = Select2ManyToManyField(
        Author, verbose_name="Authors (AJAX full name search)", ajax=True,
        search_field=lambda q: Q(first_name__icontains=q) | Q(last_name__icontains=q),
        db_table="tests_book_authors_full_name_ajax", related_name="book_set4",
        **authors_kwargs)

    class Meta:
        ordering = ('title',)

    def __str__(self):
        return self.title
