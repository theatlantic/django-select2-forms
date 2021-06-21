from django.contrib import admin

from .models import Publisher, Author, Book, Library


class BookInline(admin.StackedInline):
    model = Book
    extra = 0


@admin.register(Library)
class LibraryAdmin(admin.ModelAdmin):
    inlines = [BookInline]


admin.site.register(Publisher)
admin.site.register(Author)
admin.site.register(Book)
