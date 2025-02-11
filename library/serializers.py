from rest_framework.serializers import ModelSerializer
from .models import User, Fine, Borrowing, Book, Genre
from django.contrib.auth.models import Group


class GroupSerializer(ModelSerializer):
    class Meta:
        model = Group
        fields = ["id", "name"]


class UserSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'password', 'email', 'groups']


class FineSerializer(ModelSerializer):
    class Meta:
        model = Fine
        fields = '__all__'


class BookSerializer(ModelSerializer):
    class Meta:
        model = Book
        fields = '__all__'


class BorrowingSerializer(ModelSerializer):
    class Meta:
        model = Borrowing
        fields = '__all__'


class GenreSerializer(ModelSerializer):
    class Meta:
        model = Genre
        fields = '__all__'
