from django.conf import settings
from django.contrib import admin

from .models import Publisher, Author, Book, Library


class BookInline(admin.StackedInline):
    model = Book
    extra = 0

    @property
    def classes(self):
        if "grappelli" in settings.INSTALLED_APPS:
            return ("grp-collapse grp-open",)
        else:
            return None

    @property
    def inline_classes(self):
        return self.classes


@admin.register(Library)
class LibraryAdmin(admin.ModelAdmin):
    inlines = [BookInline]


admin.site.register(Publisher)
admin.site.register(Author)
admin.site.register(Book)
