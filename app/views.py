from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from .models import Book, Author
from .serializers import BookSerializer, AuthorSerializer


class BookPagination(PageNumberPagination):
    page_size = 10


class BookViewSet(viewsets.ModelViewSet):
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    pagination_class = BookPagination

    def get_queryset(self):
        author_id = self.request.query_params.get("author", None)
        if author_id:
            return self.queryset.filter(author_id=author_id)
        return self.queryset

    @action(detail=True, methods=["post"])
    def buy(self, request, pk=None):
        book = self.get_object()
        if book.count > 0:
            book.count -= 1
            book.save()
            return Response(
                {"message": "Book purchased successfully!"}, status=status.HTTP_200_OK
            )
        return Response(
            {"error": "Book out of stock!"}, status=status.HTTP_400_BAD_REQUEST
        )


class AuthorViewSet(viewsets.ModelViewSet):
    queryset = Author.objects.all()
    serializer_class = AuthorSerializer
