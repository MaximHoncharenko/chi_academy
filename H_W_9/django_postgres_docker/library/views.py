from django.views.generic import ListView
from django.db.models import Count
from .models import Author, Book


class AuthorListView(ListView):
    """Представлення для списку авторів з підрахунком книг"""
    model = Author
    template_name = 'library/authors.html'
    context_object_name = 'authors'
    
    def get_queryset(self):
        # Анотація: підрахунок кількості книг для кожного автора
        return Author.objects.annotate(books_count=Count('books')).order_by('name')


class BookListView(ListView):
    """Представлення для списку всіх книг"""
    model = Book
    template_name = 'library/books.html'
    context_object_name = 'books'
    
    def get_queryset(self):
        # Використання select_related для оптимізації запитів
        return Book.objects.select_related('author').order_by('-published_date')


class AuthorBooksView(ListView):
    """Представлення для книг конкретного автора"""
    model = Book
    template_name = 'library/author_books.html'
    context_object_name = 'books'
    
    def get_queryset(self):
        # Фільтрація книг за автором
        author_id = self.kwargs.get('author_id')
        return Book.objects.filter(author_id=author_id).select_related('author').order_by('-published_date')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Додаємо інформацію про автора в контекст
        author_id = self.kwargs.get('author_id')
        context['author'] = Author.objects.get(id=author_id)
        return context
