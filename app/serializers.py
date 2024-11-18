from rest_framework import serializers
from .models import Book, Author


class BookSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = ["id", "title", "count", "author"]


class AuthorSerializer(serializers.ModelSerializer):
    books = serializers.SerializerMethodField()

    class Meta:
        model = Author
        fields = ["id", "first_name", "last_name", "books"]

    def get_books(self, obj):
        books = Book.objects.filter(author=obj)
        return [book.title for book in books]
