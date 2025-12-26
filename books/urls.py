from django.urls import path
from . import views

app_name = 'books'

urlpatterns = [
    path('my-books/', views.my_books, name='my_books'),
    path('', views.BookListView.as_view(), name='book_list'),
    path('book/<int:pk>/', views.BookDetailView.as_view(), name='book_detail'),
    path('book/add/', views.book_create, name='book_add'),
    path('book/<int:pk>/edit/', views.book_update, name='book_edit'),
    path('book/<int:pk>/delete/', views.book_delete, name='book_delete'),
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('book/<int:pk>/download/', views.download_pdf, name='download_pdf'),
    path('export/mybooks/', views.export_mybooks_pdf, name='export_mybooks_pdf'),
    path('book/<int:pk>/export/', views.export_book_pdf, name='export_book_pdf'),
]
