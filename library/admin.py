from django.contrib import admin
from .models import User, Borrowing, Book, Fine, Genre

# Register your models here.
admin.site.register(User)
admin.site.register(Borrowing)
admin.site.register(Book)
admin.site.register(Fine)
admin.site.register(Genre)
