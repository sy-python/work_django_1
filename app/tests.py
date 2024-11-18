from rest_framework.test import APITestCase
from rest_framework import status
from .models import Book, Author


class BookshopAPITests(APITestCase):
    def setUp(self):
        """
        Set up test data for the API.
        """
        self.author1 = Author.objects.create(first_name="Sy", last_name="Python")
        self.author2 = Author.objects.create(first_name="Sarah Jane", last_name="Smith")
        self.author3 = Author.objects.create(first_name="John", last_name="Doe")
        self.author4 = Author.objects.create(first_name="Writer's", last_name="Block")

        self.book1 = Book.objects.create(
            title="My Deeds, My Powers, My Achievements and the Injustices Perpetrated Against Me",
            author=self.author1,
            count=10,
        )
        self.book2 = Book.objects.create(
            title="History Of Everything", author=self.author1, count=0
        )
        self.book3 = Book.objects.create(
            title="U.N.I.T. Training Course", author=self.author2, count=5
        )
        self.john_books = []
        for i in range(50):
            book = Book.objects.create(title=f"Book {i}", author=self.author3, count=i)
            self.john_books.append(book)

    def test_list_books(self):
        first_page_response = self.client.get("/api/books/")

        self.assertEqual(first_page_response.status_code, status.HTTP_200_OK)

        first_page_data = first_page_response.json()

        self.assertEqual(first_page_data["count"], 53)
        self.assertIn("next", first_page_data)

        first_page = first_page_data["results"]
        first_page_titles = [book["title"] for book in first_page]

        self.assertIn(
            "My Deeds, My Powers, My Achievements and the Injustices Perpetrated Against Me",
            first_page_titles,
        )
        self.assertIn("History Of Everything", first_page_titles)
        self.assertIn("U.N.I.T. Training Course", first_page_titles)

        self.assertEqual(len(first_page), 10)

        sixth_page_response = self.client.get("/api/books/?page=6")
        sixth_page_data = sixth_page_response.json()
        sixth_page = sixth_page_data["results"]

        self.assertEqual(len(sixth_page), 3)

        sixth_page_titles = [book["title"] for book in sixth_page]

        self.assertEqual(
            sixth_page_titles,
            [
                "Book 47",
                "Book 48",
                "Book 49",
            ],
        )

        negative_page_response = self.client.get("/api/books/?page=-1")
        large_page_response = self.client.get("/api/books/?page=1000")

        self.assertEqual(negative_page_response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(large_page_response.status_code, status.HTTP_404_NOT_FOUND)

        negative_page_data = negative_page_response.json()
        larg_page_data = large_page_response.json()

        self.assertEqual(negative_page_data["detail"], "Invalid page.")
        self.assertEqual(larg_page_data["detail"], "Invalid page.")

    def test_filter_books(self):
        sy_books_response = self.client.get(f"/api/books/?author={self.author1.id}")

        self.assertEqual(sy_books_response.status_code, status.HTTP_200_OK)

        sy_books_data = sy_books_response.json()

        self.assertEqual(sy_books_data["count"], 2)

        sy_books = sy_books_data["results"]
        sy_books_titles = [book["title"] for book in sy_books]

        self.assertEqual(
            sy_books_titles,
            [
                "My Deeds, My Powers, My Achievements and the Injustices Perpetrated Against Me",
                "History Of Everything",
            ],
        )

        john_books_response = self.client.get(f"/api/books/?author={self.author3.id}")

        self.assertEqual(john_books_response.status_code, status.HTTP_200_OK)

        john_books_data = john_books_response.json()

        self.assertEqual(john_books_data["count"], 50)

        john_books = john_books_data["results"]
        john_books_titles = [book["title"] for book in john_books]

        self.assertEqual(
            john_books_titles,
            [f"Book {i}" for i in range(10)],
        )

        block_books_response = self.client.get(f"/api/books/?author={self.author4.id}")

        self.assertEqual(block_books_response.status_code, status.HTTP_200_OK)

        block_books_data = block_books_response.json()

        self.assertEqual(block_books_data["count"], 0)

        invalid_author_response = self.client.get(f"/api/books/?author=1234")

        self.assertEqual(invalid_author_response.status_code, status.HTTP_200_OK)

        invalid_author_data = invalid_author_response.json()

        self.assertEqual(invalid_author_data["count"], 0)

    def test_add_book(self):
        book_1 = {"title": "The Known Unknown", "author": self.author1.id, "count": 2}
        book_2 = {"title": "Book 50", "author": self.author3.id}

        response_1 = self.client.post("/api/books/", book_1, format="json")

        self.assertEqual(response_1.status_code, status.HTTP_201_CREATED)

        self.assertEqual(Book.objects.count(), 54)

        book_1_id = response_1.json()["id"]
        book_1_obj = Book.objects.get(id=book_1_id)

        self.assertEqual(book_1_obj.title, "The Known Unknown")
        self.assertEqual(book_1_obj.author, self.author1)
        self.assertEqual(book_1_obj.count, 2)

        response_2 = self.client.post("/api/books/", book_2, format="json")

        self.assertEqual(response_2.status_code, status.HTTP_201_CREATED)

        self.assertEqual(Book.objects.count(), 55)

        book_2_id = response_2.json()["id"]
        book_2_obj = Book.objects.get(id=book_2_id)

        self.assertEqual(book_2_obj.title, "Book 50")
        self.assertEqual(book_2_obj.author, self.author3)
        self.assertEqual(book_2_obj.count, 0)

        book_no_title = {"author": self.author1.id, "count": 2}
        book_no_author = {"title": "Who Wrote This Book?", "count": 234}
        book_negative_count = {
            "title": "The Anti-Book",
            "author": self.author1.id,
            "count": -1,
        }
        book_invalid_author = {
            "title": "No, Really, Who Wrote This Book?",
            "author": 1234,
            "count": 777,
        }
        book_completely_wrong_json = {
            "question": "The Question of Life, the Universe, and Everything",
            "answer": "42",
        }

        response_1 = self.client.post("/api/books/", book_no_title, format="json")
        response_2 = self.client.post("/api/books/", book_no_author, format="json")
        response_3 = self.client.post("/api/books/", book_negative_count, format="json")
        response_4 = self.client.post("/api/books/", book_invalid_author, format="json")
        response_5 = self.client.post(
            "/api/books/", book_completely_wrong_json, format="json"
        )

        self.assertEqual(response_1.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response_2.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response_3.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response_4.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response_5.status_code, status.HTTP_400_BAD_REQUEST)

        self.assertEqual(Book.objects.count(), 55)

        response_1_data = response_1.json()
        response_2_data = response_2.json()
        response_3_data = response_3.json()
        response_4_data = response_4.json()
        response_5_data = response_5.json()

        self.assertEqual(response_1_data["title"], ["This field is required."])
        self.assertEqual(response_2_data["author"], ["This field is required."])
        self.assertEqual(
            response_3_data["count"],
            ["Ensure this value is greater than or equal to 0."],
        )
        self.assertEqual(
            response_4_data["author"], ['Invalid pk "1234" - object does not exist.']
        )
        self.assertEqual(response_5_data["title"], ["This field is required."])
        self.assertEqual(response_5_data["author"], ["This field is required."])

    def test_update_book(self):
        book = {
            "title": "My Deeds, My Powers, My Achievements and the Injustices Perpetrated Against Me (Redacted Version)",
            "author": self.author1.id,
            "count": 200,
        }

        response = self.client.put(f"/api/books/{self.book1.id}/", book, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        book_obj = Book.objects.get(id=self.book1.id)

        self.assertEqual(
            book_obj.title,
            "My Deeds, My Powers, My Achievements and the Injustices Perpetrated Against Me (Redacted Version)",
        )
        self.assertEqual(book_obj.author, self.author1)
        self.assertEqual(book_obj.count, 200)

        book_bad_json = {
            "question": "The Question of Life, the Universe, and Everything",
            "answer": "42",
        }

        bad_response = self.client.put(
            f"/api/books/{self.book2.id}/", book_bad_json, format="json"
        )

        self.assertEqual(bad_response.status_code, status.HTTP_400_BAD_REQUEST)

        bad_data = bad_response.json()

        self.assertEqual(bad_data["title"], ["This field is required."])
        self.assertEqual(bad_data["author"], ["This field is required."])

        book_obj = Book.objects.get(id=self.book2.id)

        self.assertEqual(book_obj.title, "History Of Everything")
        self.assertEqual(book_obj.author, self.author1)
        self.assertEqual(book_obj.count, 0)

    def test_buy_book(self):
        response_with_stock = self.client.post(f"/api/books/{self.book1.id}/buy/")

        self.assertEqual(response_with_stock.status_code, status.HTTP_200_OK)

        data_with_stock = response_with_stock.json()

        self.assertEqual(data_with_stock["message"], "Book purchased successfully!")

        self.book1.refresh_from_db()

        self.assertEqual(self.book1.count, 9)

        response_no_stock = self.client.post(f"/api/books/{self.book2.id}/buy/")

        self.assertEqual(response_no_stock.status_code, status.HTTP_400_BAD_REQUEST)

        data_no_stock = response_no_stock.json()

        self.assertEqual(data_no_stock["error"], "Book out of stock!")

        response_no_book = self.client.post("/api/books/999999/buy/")

        self.assertEqual(response_no_book.status_code, status.HTTP_404_NOT_FOUND)

        data_no_book = response_no_book.json()

        self.assertEqual(data_no_book["detail"], "No Book matches the given query.")

    def test_list_authors(self):
        response = self.client.get("/api/authors/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.json()

        self.assertEqual(len(data), 4)

        first_author = data[0]

        self.assertEqual(first_author["first_name"], "Sy")
        self.assertEqual(first_author["last_name"], "Python")
        self.assertEqual(
            first_author["books"],
            [
                "My Deeds, My Powers, My Achievements and the Injustices Perpetrated Against Me",
                "History Of Everything",
            ],
        )

        john_author = data[2]

        self.assertEqual(john_author["books"], [f"Book {i}" for i in range(50)])

    def test_add_author(self):
        new_author = {"first_name": "Ivan", "last_name": "Ivanov"}

        good_response = self.client.post("/api/authors/", new_author, format="json")

        self.assertEqual(good_response.status_code, status.HTTP_201_CREATED)

        data = good_response.json()

        self.assertEqual(data["first_name"], "Ivan")
        self.assertEqual(data["last_name"], "Ivanov")

        check_response = self.client.get("/api/authors/")
        check_data = check_response.json()

        self.assertEqual(len(check_data), 5)

        fresh_author = Author.objects.get(first_name="Ivan", last_name="Ivanov")

        self.assertTrue(fresh_author)

        bad_author = {"name": "Dimitri Dimitriyevich"}
        response = self.client.post("/api/authors/", bad_author, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data = response.json()

        self.assertEqual(data["first_name"], ["This field is required."])
        self.assertEqual(data["last_name"], ["This field is required."])

        bad_fresh_author = Author.objects.filter(
            first_name="Dimitri", last_name="Dimitriyevich"
        )

        self.assertFalse(bad_fresh_author)

    def test_update_author(self):
        new_author = {"first_name": "Rostislav", "last_name": "Gerasenko"}

        good_response = self.client.put(
            f"/api/authors/{self.author1.id}/", new_author, format="json"
        )

        self.assertEqual(good_response.status_code, status.HTTP_200_OK)

        self.author1.refresh_from_db()

        self.assertEqual(self.author1.first_name, "Rostislav")
        self.assertEqual(self.author1.last_name, "Gerasenko")

        bad_response = self.client.put(
            f"/api/authors/999999/", new_author, format="json"
        )

        self.assertEqual(bad_response.status_code, status.HTTP_404_NOT_FOUND)

        data = bad_response.json()

        self.assertEqual(data["detail"], "No Author matches the given query.")
