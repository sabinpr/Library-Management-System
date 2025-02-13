from django.contrib.auth.models import AbstractUser, Group
from django.core.exceptions import ValidationError
from datetime import date
from django.db import models
from django.utils.timezone import now

# Create your models here.


# Custom Manager for Borrowing Model
class BorrowingManager(models.Manager):

    # Return borrowings that are still active(not returned)
    def active_borrowings(self):
        return self.filter(returned=False)

    # Return borrowings that are overdue
    def overdue_borrowings(self):
        return self.filter(due_date__lt=date.today(), returned=False)

# Custom User Model


class User(AbstractUser):
    username = models.CharField(max_length=200, blank=True, default="")
    password = models.CharField(max_length=200)
    email = models.EmailField(unique=True)
    groups = models.ForeignKey(
        Group, on_delete=models.SET_NULL, null=True, blank=True)

    # Make email default username
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']


# Genre Model (for Book Categories)
class Genre(models.Model):

    # Name of the genre
    name = models.CharField(max_length=100, unique=True)

    # Descriuption of the genre
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name


# Book Model (for Book in the library)
class Book(models.Model):
    # Title of the book
    title = models.CharField(max_length=255)
    # Author of the book
    author = models.CharField(max_length=255)
    # Many-to-Many Reltionship with Genre
    genre = models.ManyToManyField(Genre, related_name="books")
    # ISBN field for the book
    isbn = models.CharField(max_length=13, unique=True)
    # Description of the book
    description = models.TextField(blank=True, null=True)
    # publisher of the book
    publisher = models.CharField(max_length=255, blank=True, null=True)
    # published_date of the book
    published_date = models.DateField(blank=True, null=True)
    # total copies available
    total_copies = models.PositiveIntegerField(default=1)
    # total borrowed books
    borrowed_copies = models.PositiveIntegerField(default=0)

    # Property to calculate the number of available copies
    @property
    def available_copies(self):
        return self.total_copies-self.borrowed_copies

    def __str__(self):
        return f'{self.title} by {self.author}'


# Borrowing Model to track book borrowing information
class Borrowing(models.Model):
    # the member who borroowed the book
    member = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True)
    # the book that was borrowed
    book = models.ForeignKey(
        Book, on_delete=models.SET_NULL, null=True, blank=True)
    # when the book was borrowed
    borrowed_at = models.DateTimeField(auto_now_add=True)
    # when the book was returned
    returned_at = models.DateTimeField(null=True, blank=True)
    # deadline for returning book
    due_date = models.DateField()
    # whether the book has been retured or not
    returned = models.BooleanField(default=False)

    objects = BorrowingManager()

    def save(self, *args, **kwargs):
        # Update borrowed_copies when a book is borrowed or returned
        if not self.pk:  # New borrow instance
            if self.book and self.book.available_copies > 0:
                self.book.borrowed_copies += 1
            else:
                raise ValidationError("No copies available to borrow!")
        # Set returned_at automatically when returned is marked True
        elif self.returned and not self.returned_at:  # Mark as returned
            self.returned_at = now()  # Set returned_at to current time
            if self.book:
                self.book.borrowed_copies = max(
                    0, self.book.borrowed_copies - 1)  # Prevent negative values

        if self.book:
            self.book.save()  # Save book changes
        super().save(*args, **kwargs)

    # Ensure due date is not before borrow date
    def clean(self):
        if self.borrowed_at and self.due_date < self.borrowed_at.date():
            raise ValidationError(
                'Due date cannot be before the borrowed date')

    def __str__(self):
        return f"{self.member.username} - {self.book.title}"


# Fine Model - Charges Fine if the book is returned late
class Fine(models.Model):
    # Borrowing record one-to-one relationship with fine
    borrowing = models.OneToOneField(Borrowing, on_delete=models.CASCADE)
    # Fine for overdue books
    fine_amount = models.DecimalField(
        max_digits=6, decimal_places=2, default=0)
    # Fine is paid or not paid
    paid = models.BooleanField(default=False)
    # Date and time when fine  was created
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Fine for {self.borrowing.book.title} - Rs.{self.fine_amount}"

    # Methood to calculate fine based on overdue days
    def calculate_fine(self):
        if not self.borrowing.returned:  # Only apply fine if book is still borrowed
            overdue_days = (date.today() - self.borrowing.due_date).days
            # Rs.10 per overdue day
            self.fine_amount = max(0, overdue_days * 10)
            self.save()
