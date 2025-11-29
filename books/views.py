from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import FileResponse, HttpResponse, HttpResponseForbidden
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView
from django.conf import settings
from .models import Book, Genre
from .forms import RegisterForm, BookForm

# Регистрация
def register_view(request):
    if request.user.is_authenticated:
        return redirect('books:book_list')
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Регистрация прошла успешно.')
            return redirect('books:book_list')
    else:
        form = RegisterForm()
    return render(request, 'books/register.html', {'form': form})

# Используем встроенные представления для входа/выхода либо напишем свои простые
from django.contrib.auth.forms import AuthenticationForm
def login_view(request):
    if request.user.is_authenticated:
        return redirect('books:book_list')
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('books:book_list')
    else:
        form = AuthenticationForm()
    return render(request, 'books/login.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('books:book_list')

# Список книг: все пользователи видят список
class BookListView(ListView):
    model = Book
    template_name = 'books/book_list.html'
    context_object_name = 'books'
    paginate_by = 12
    ordering = ['-created_at']

# Детальная страница
class BookDetailView(DetailView):
    model = Book
    template_name = 'books/book_detail.html'
    context_object_name = 'book'

# Создать книгу (только для авторизованных)
@login_required
def book_create(request):
    if request.method == 'POST':
        form = BookForm(request.POST, request.FILES)
        if form.is_valid():
            book = form.save(commit=False)
            book.owner = request.user
            book.save()
            messages.success(request, 'Книга добавлена.')
            return redirect('books:book_detail', pk=book.pk)
    else:
        form = BookForm()
    return render(request, 'books/book_form.html', {'form': form})

# Редактировать — только владелец
@login_required
def book_update(request, pk):
    book = get_object_or_404(Book, pk=pk)
    if book.owner != request.user:
        return HttpResponseForbidden("Недостаточно прав")
    if request.method == 'POST':
        form = BookForm(request.POST, request.FILES, instance=book)
        if form.is_valid():
            form.save()
            messages.success(request, 'Книга обновлена.')
            return redirect('books:book_detail', pk=book.pk)
    else:
        form = BookForm(instance=book)
    return render(request, 'books/book_form.html', {'form': form, 'book': book})

# Удалить — только владелец
@login_required
def book_delete(request, pk):
    book = get_object_or_404(Book, pk=pk)
    if book.owner != request.user:
        return HttpResponseForbidden("Недостаточно прав")
    if request.method == 'POST':
        book.delete()
        messages.success(request, 'Книга удалена.')
        return redirect('books:book_list')
    return render(request, 'books/book_confirm_delete.html', {'book': book})

# Скачивание PDF — только для авторизованных
from wsgiref.util import FileWrapper
import os

@login_required
def download_pdf(request, pk):
    book = get_object_or_404(Book, pk=pk)
    file_path = book.pdf_file.path
    # На проде использовать X-Sendfile / nginx internal; для разработки используем FileResponse
    if os.path.exists(file_path):
        response = FileResponse(open(file_path, 'rb'), as_attachment=True, filename=os.path.basename(file_path))
        return response
    return HttpResponse("Файл не найден", status=404)

# Экспорт списка книг пользователя в PDF (ReportLab)
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from io import BytesIO

@login_required
def export_mybooks_pdf(request):
    buffer = BytesIO()
    p = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4
    y = height - 50
    p.setFont("Helvetica-Bold", 16)
    p.drawString(50, y, f"Книги пользователя: {request.user.get_full_name() or request.user.username}")
    y -= 30
    p.setFont("Helvetica", 12)
    books = request.user.books.all().order_by('-created_at')
    for book in books:
        if y < 80:
            p.showPage()
            y = height - 50
        p.drawString(60, y, f"• {book.title} — {book.author} ({book.year or '—'}) [{book.genre}]")
        y -= 18
    p.showPage()
    p.save()
    buffer.seek(0)
    return FileResponse(buffer, as_attachment=True, filename='my_books.pdf', content_type='application/pdf')

# Экспорт детальной страницы книги в PDF
@login_required
def export_book_pdf(request, pk):
    book = get_object_or_404(Book, pk=pk)
    buffer = BytesIO()
    p = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4
    y = height - 50
    p.setFont("Helvetica-Bold", 18)
    p.drawString(50, y, book.title)
    y -= 30
    p.setFont("Helvetica", 12)
    p.drawString(50, y, f"Автор: {book.author}")
    y -= 18
    p.drawString(50, y, f"Год: {book.year or '—'}  Жанр: {book.genre or '—'}  Возраст: {book.age_category}")
    y -= 30
    p.setFont("Helvetica", 11)
    lines = book.description.splitlines()
    for line in lines:
        if y < 80:
            p.showPage()
            y = height - 50
        p.drawString(50, y, line)
        y -= 16
    p.showPage()
    p.save()
    buffer.seek(0)
    safe_title = ''.join(c for c in book.title if c.isalnum() or c in (' ', '_')).rstrip()
    return FileResponse(buffer, as_attachment=True, filename=f'{safe_title}.pdf', content_type='application/pdf')
