from django.contrib import admin
from .models import Book, Genre

@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'owner', 'genre', 'year', 'age_category', 'created_at')
    search_fields = ('title', 'author', 'owner__username')
    list_filter = ('genre', 'age_category')

@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    list_display = ('name',)
