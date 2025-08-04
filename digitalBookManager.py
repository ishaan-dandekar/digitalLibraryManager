import json
from datetime import datetime


class Person:

    def __init__(self, user_id, name):
        self.user_id = user_id
        self.name = name
        self.borrowed_books = []


class Student(Person):

    def __init__(self, user_id, name):
        super().__init__(user_id, name)
        self.user_type = "Student"
        self.max_books = 3

    # dont mess with this logic - took me a while to get it working ~Ishaan
    def get_year(self):
        current_year = datetime.now().year
        admission_year = 2000 + int(str(self.user_id)[:2])
        year_diff = current_year - admission_year

        match year_diff:
            case 0:
                return "FE"
            case 1:
                return "SE"
            case 2:
                return "TE"
            case 3:
                return "BE"
            case _:
                return "Graduate"

    def get_branch(self):
        branch_map = {1: "Comps", 2: "IT", 3: "AIML", 4: "DS"}
        branch_digit = int(str(self.user_id)[2])
        return branch_map.get(branch_digit, "Unknown")

    def get_division(self):
        division_map = {0: "A", 1: "B", 2: "C"}
        division_digit = int(str(self.user_id)[3])
        return division_map.get(division_digit, "Unknown")


class Faculty(Person):

    def __init__(self, user_id, name):
        super().__init__(user_id, name)
        self.user_type = "Faculty"
        self.max_books = 5


class Book:

    def __init__(self, isbn, title, author, total_count=1):
        self.isbn = isbn
        self.title = title
        self.author = author
        self.total_count = total_count
        self.available_count = total_count
        self.borrowed_by = []


class LibraryManager:

    def __init__(self):
        self.users = {}
        self.books = {}
        self.load_data()

    def load_data(self):
        try:
            with open('users.json', 'r') as f:
                users_data = json.load(f)
                for user_data in users_data:
                    if len(str(user_data['id'])) == 8:
                        user = Student(user_data['id'], user_data['name'])
                    else:
                        user = Faculty(user_data['id'], user_data['name'])

                    user.borrowed_books = user_data.get('borrowed_books', [])
                    self.users[user.user_id] = user
        except FileNotFoundError:
            pass

        try:
            with open('books.json', 'r') as f:
                books_data = json.load(f)
                for book_data in books_data:
                    book = Book(book_data['isbn'], book_data['title'],
                                book_data['author'], book_data['total_count'])
                    book.available_count = book_data.get('available_count', book.total_count)
                    book.borrowed_by = book_data.get('borrowed_tby', [])
                    self.books[book.isbn] = book
        except FileNotFoundError:
            pass

    def save_data(self):
        users_data = []
        for user in self.users.values():
            users_data.append({
                'id': user.user_id,
                'name': user.name,
                'borrowed_books': user.borrowed_books
            })

        with open('users.json', 'w') as f:
            json.dump(users_data, f, indent=2)

        books_data = []
        for book in self.books.values():
            books_data.append({
                'isbn': book.isbn,
                'title': book.title,
                'author': book.author,
                'total_count': book.total_count,
                'available_count': book.available_count,
                'borrowed_by': book.borrowed_by
            })

        with open('books.json', 'w') as f:
            json.dump(books_data, f, indent=2)

    def add_user(self):
        try:
            user_id = int(input("Enter user ID: "))
        except ValueError:
            print("Invalid user ID! Please enter a numeric ID.")
            return

        name = input("Enter name: ")

        if len(str(user_id)) == 8:
            user = Student(user_id, name)
            print(f"Student added: {name} ({user.get_year()} {user.get_branch()} {user.get_division()})")
        elif len(str(user_id)) == 3:
            user = Faculty(user_id, name)
            print(f"Faculty added: {name}")
        else:
            print("Invalid ID format! Student IDs must be 8 digits, Faculty IDs must be 3 digits.")
            return

        self.users[user_id] = user
        self.save_data()

    def add_book(self):
        isbn = input("Enter ISBN: ")
        title = input("Enter title: ")
        author = input("Enter author: ")

        try:
            count = int(input("Enter number of copies: "))
        except ValueError:
            print("Invalid number of copies! Please enter a valid number.")
            return

        if isbn in self.books:
            self.books[isbn].total_count += count
            self.books[isbn].available_count += count
            print(f"Updated book count for '{title}' - Added {count} copies")
        else:
            book = Book(isbn, title, author, count)
            self.books[isbn] = book
            print(f"Book '{title}' added successfully with {count} copies!")

        self.save_data()

    def issue_book(self):
        try:
            user_id = int(input("Enter user ID: "))
        except ValueError:
            print("Invalid user ID! Please enter a numeric ID.")
            return

        isbn = input("Enter book ISBN: ")

        if user_id not in self.users:
            print("User not found!")
            return

        if isbn not in self.books:
            print("Book not found!")
            return

        book = self.books[isbn]
        user = self.users[user_id]

        # Please dont touch this part, the book issuing logic is sensitive! Thanks :) ~Arya
        # Don't worry i got it backed up to a git repo now
        if book.available_count <= 0:
            print("Book not available!")
            return

        if isbn in user.borrowed_books:
            print("User already has this book!")
            return

        if len(user.borrowed_books) >= user.max_books:
            print(f"Cannot issue book! {user.user_type} borrowing limit ({user.max_books} books) reached.")
            return

        book.available_count -= 1
        book.borrowed_by.append(user_id)
        user.borrowed_books.append(isbn)

        print(f"Book '{book.title}' issued to {user.name}")
        self.save_data()

    def return_book(self):
        try:
            user_id = int(input("Enter user ID: "))
        except ValueError:
            print("Invalid user ID! Please enter a numeric ID.")
            return

        isbn = input("Enter book ISBN: ")

        if user_id not in self.users:
            print("User not found!")
            return

        if isbn not in self.books:
            print("Book not found!")
            return

        book = self.books[isbn]
        user = self.users[user_id]

        if isbn not in user.borrowed_books:
            print("User doesn't have this book!")
            return

        book.available_count += 1
        book.borrowed_by.remove(user_id)
        user.borrowed_books.remove(isbn)

        print(f"Book '{book.title}' returned by {user.name}")
        self.save_data()

    def display_user_info(self):
        try:
            user_id = int(input("Enter user ID: "))
        except ValueError:
            print("Invalid user ID! Please enter a numeric ID.")
            return

        if user_id not in self.users:
            print("User not found!")
            return

        user = self.users[user_id]
        print(f"\n--- User Information ---")
        print(f"ID: {user.user_id}")
        print(f"Name: {user.name}")
        print(f"Type: {user.user_type}")

        if isinstance(user, Student):
            print(f"Year: {user.get_year()}")
            print(f"Branch: {user.get_branch()}")
            print(f"Division: {user.get_division()}")

        print(f"Borrowing limit: {user.max_books} books")
        print(f"Currently borrowed books: {len(user.borrowed_books)}/{user.max_books}")
        for isbn in user.borrowed_books:
            if isbn in self.books:
                book = self.books[isbn]
                print(f"  - {book.title}")
            else:
                print(f"  - Book with ISBN {isbn} (Book details not found)")

        input("\nPress Enter to continue...")

    def display_book_info(self):
        isbn = input("Enter book ISBN: ")

        if isbn not in self.books:
            print("Book not found!")
            return

        book = self.books[isbn]
        print(f"\n--- Book Information ---")
        print(f"ISBN: {book.isbn}")
        print(f"Title: {book.title}")
        print(f"Author: {book.author}")
        print(f"Total copies: {book.total_count}")
        print(f"Available copies: {book.available_count}")
        print(f"Currently borrowed by {len(book.borrowed_by)} users")

        if book.borrowed_by:
            print("Borrowed by:")
            for user_id in book.borrowed_by:
                user = self.users[user_id]
                print(f"  - {user.name} (ID: {user_id})")

        input("\nPress Enter to continue...")

    def search_books(self):
        query = input("Enter title or author to search: ").lower()
        found_books = []

        for book in self.books.values():
            if query in book.title.lower() or query in book.author.lower():
                found_books.append(book)

        if not found_books:
            print("No books found!")
            return

        print(f"\n--- Search Results ({len(found_books)} books found) ---")
        for book in found_books:
            print(
                f"ISBN: {book.isbn} | Title: {book.title} | Author: {book.author} | Available: {book.available_count}/{book.total_count}")

    def list_issued_books(self):
        print("\n--- Currently Issued Books ---")
        issued_found = False

        for user in self.users.values():
            if user.borrowed_books:
                for isbn in user.borrowed_books:
                    if isbn in self.books:
                        book = self.books[isbn]
                        print(
                            f"Book: {book.title} | Author: {book.author} | Borrowed by: {user.name} (ID: {user.user_id})")
                        issued_found = True
                    else:
                        print(
                            f"Book with ISBN {isbn} | Borrowed by: {user.name} (ID: {user.user_id}) | (Book details not found)")
                        issued_found = True

        if not issued_found:
            print("No books are currently issued!")

        input("\nPress Enter to continue...")

    filter_available_books = lambda self: [book for book in self.books.values() if book.available_count > 0]

    def run(self):
        while True:
            print("\n=== Digital Library Management System ===")
            print("1. Add User")
            print("2. Add Book")
            print("3. Issue Book")
            print("4. Return Book")
            print("5. Display User Info")
            print("6. Display Book Info")
            print("7. Search Books")
            print("8. List Available Books")
            print("9. List Issued Books")
            print("0. Exit")

            try:
                choice = int(input("\nEnter your choice: "))

                match choice:
                    case 1:
                        self.add_user()
                    case 2:
                        self.add_book()
                    case 3:
                        self.issue_book()
                    case 4:
                        self.return_book()
                    case 5:
                        self.display_user_info()
                    case 6:
                        self.display_book_info()
                    case 7:
                        self.search_books()
                    case 8:
                        available_books = self.filter_available_books()
                        print(f"\n--- Available Books ({len(available_books)}) ---")
                        for book in available_books:
                            print(f"{book.title} by {book.author} - {book.available_count} copies available")
                        input("\nPress Enter to continue...")
                    case 9:
                        self.list_issued_books()
                    case 0:
                        print("Thank you for using the Library Management System!")
                        break
                    case _:
                        print("Invalid choice! Please try again.")

            except ValueError:
                print("Please enter a valid number!")
            except Exception as e:
                print(f"An error occurred: {e}")


if __name__ == "__main__":
    library = LibraryManager()
    library.run()
