from django.db import models


class Author(models.Model):
    """Модель Автора"""
    name = models.CharField(max_length=200, verbose_name="Ім'я автора")
    email = models.EmailField(blank=True, null=True, verbose_name="Email")
    bio = models.TextField(blank=True, null=True, verbose_name="Біографія")

    class Meta:
        verbose_name = "Автор"
        verbose_name_plural = "Автори"
        ordering = ['name']

    def __str__(self):
        return self.name


class Book(models.Model):
    """Модель Книги"""
    title = models.CharField(max_length=300, verbose_name="Назва книги")
    description = models.TextField(verbose_name="Опис")
    published_date = models.DateField(verbose_name="Дата публікації")
    author = models.ForeignKey(
        Author,
        on_delete=models.CASCADE,
        related_name='books',
        verbose_name="Автор"
    )

    class Meta:
        verbose_name = "Книга"
        verbose_name_plural = "Книги"
        ordering = ['-published_date']  # Нові книги першими

    def __str__(self):
        return self.title
