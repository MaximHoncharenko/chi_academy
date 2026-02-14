from django.contrib import admin
from .models import Author, Book


@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    """Адмін-панель для Авторів"""
    list_display = ('name', 'email', 'get_books_count')
    search_fields = ('name', 'email')
    list_filter = ('name',)
    
    def get_books_count(self, obj):
        return obj.books.count()
    
    get_books_count.short_description = 'Кількість книг'


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    """Адмін-панель для Книг"""
    list_display = ('title', 'author', 'published_date')
    search_fields = ('title', 'description', 'author__name')
    list_filter = ('published_date', 'author')
    date_hierarchy = 'published_date'
    autocomplete_fields = ['author']
    
    fieldsets = (
        ('Основна інформація', {
            'fields': ('title', 'author')
        }),
        ('Деталі', {
            'fields': ('description', 'published_date')
        }),
    )
