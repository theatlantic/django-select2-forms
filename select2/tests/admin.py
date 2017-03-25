from django.contrib import admin

from .models import Publisher, Author, Book


admin.site.register([Publisher, Author, Book], admin.ModelAdmin)
