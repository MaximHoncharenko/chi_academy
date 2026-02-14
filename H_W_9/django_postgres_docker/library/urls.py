from django.urls import path
from .views import AuthorListView, BookListView, AuthorBooksView

app_name = 'library'

urlpatterns = [
    path('', AuthorListView.as_view(), name='home'),
    path('authors/', AuthorListView.as_view(), name='authors'),
    path('books/', BookListView.as_view(), name='books'),
    path('authors/<int:author_id>/books/', AuthorBooksView.as_view(), name='author_books'),
]
