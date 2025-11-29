from django.db import models
from django.contrib.auth.models import User

AGE_CHOICES = [
    ('0+', '0+'),
    ('6+', '6+'),
    ('12+', '12+'),
    ('16+', '16+'),
    ('18+', '18+'),
]

class Genre(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

class Book(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='books')
    title = models.CharField(max_length=255)
    author = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    genre = models.ForeignKey(Genre, on_delete=models.SET_NULL, null=True, blank=True)
    year = models.PositiveIntegerField(null=True, blank=True)
    age_category = models.CharField(max_length=10, choices=AGE_CHOICES, default='0+')
    cover = models.ImageField(upload_to='covers/', null=True, blank=True)
    pdf_file = models.FileField(upload_to='books_pdf/', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} — {self.author}"
