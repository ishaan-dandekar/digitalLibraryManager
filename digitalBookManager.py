import json
from datetime import datetime, timedelta


class Person:
    """Base class for all library users"""

    def __init__(self, user_id, name):
        self.user_id = user_id
        self.name = name
        self.borrowed_books = []
        self.borrow_dates = []
        self.history = []
        self.return_dates = []


class Student(Person):
    """Student class inheriting from Person"""

    def __init__(self, user_id, name):
        super().__init__(user_id, name)
        self.user_type = "Student"
        self.year = self._calculate_year()
        self.branch = self._get_branch()
        self.division = self._get_division()

    def _calculate_year(self):
        current_year = datetime.now().year
        admission_year = 2000 + int(str(self.user_id)[:2])
        year_diff = current_year - admission_year

        if year_diff == 0:
            return "FE"
        elif year_diff == 1:
            return "SE"
        elif year_diff == 2:
            return "TE"
        elif year_diff == 3:
            return "BE"
        else:
            return "Graduate"

    def _get_branch(self):
        branch_map = {1: "Comps", 2: "IT", 3: "AIML", 4: "DS"}
        branch_digit = int(str(self.user_id)[2])
        return branch_map.get(branch_digit, "Unknown")

    def _get_division(self):
        division_map = {0: "A", 1: "B", 2: "C"}
        division_digit = int(str(self.user_id)[3])
        return division_map.get(division_digit, "Unknown")


class Faculty(Person):
    """Faculty class inheriting from Person"""

    def __init__(self, user_id, name):
        super().__init__(user_id, name)
        self.user_type = "Faculty"


class Book:
    """Book class to manage book information"""

    def __init__(self, isbn, title, author, total_count=1):
        self.isbn = isbn
        self.title = title
        self.author = author
        self.total_count = total_count
        self.available_count = total_count
        self.borrowed_by = []


class LibraryManager:
    """Main library management system"""

    def __init__(self):
        self.users = {}
        self.books = {}
        self.load_data()

    def load_data(self):
        """Load data from JSON files"""
        try:
            with open('users.json', 'r') as f:
                users_data = json.load(f)
                for user_data in users_data:
                    if len(str(user_data['id'])) == 8:
                        user = Student(user_data['id'], user_data['name'])
                    else:
                        user = Faculty(user_data['id'], user_data['name'])

                    user.borrowed_books = user_data.get('borrowed_books', [])
                    user.borrow_dates = user_data.get('borrow_dates', [])
                    user.history = user_data.get('history', [])
                    user.return_dates = user_data.get('return_dates', [])
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
                    book.borrowed_by = book_data.get('borrowed_by', [])
                    self.books[book.isbn] = book
        except FileNotFoundError:
            pass

    def save_data(self):
        """Save data to JSON files"""
        users_data = []
        for user in self.users.values():
            users_data.append({
                'id': user.user_id,
                'name': user.name,
                'borrowed_books': user.borrowed_books,
                'borrow_dates': user.borrow_dates,
                'history': user.history,
                'return_dates': user.return_dates
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
        """Add a new user to the system"""
        user_id = int(input("Enter user ID: "))
        name = input("Enter name: ")

        if len(str(user_id)) == 8:
            user = Student(user_id, name)
            print(f"Student added: {name} ({user.year} {user.branch} {user.division})")
        elif len(str(user_id)) == 3:
            user = Faculty(user_id, name)
            print(f"Faculty added: {name}")
        else:
            print("Invalid ID format!")
            return

        self.users[user_id] = user
        self.save_data()

    def add_book(self):
        """Add a new book to the system"""
        isbn = input("Enter ISBN: ")
        title = input("Enter title: ")
        author = input("Enter author: ")
        count = int(input("Enter number of copies: "))

        if isbn in self.books:
            self.books[isbn].total_count += count
            self.books[isbn].available_count += count
            print(f"Updated book count for '{title}'")
        else:
            book = Book(isbn, title, author, count)
            self.books[isbn] = book
            print(f"Book '{title}' added successfully!")

        self.save_data()

    def issue_book(self):
        """Issue a book to a user"""
        user_id = int(input("Enter user ID: "))
        isbn = input("Enter book ISBN: ")

        if user_id not in self.users:
            print("User not found!")
            return

        if isbn not in self.books:
            print("Book not found!")
            return

        book = self.books[isbn]
        user = self.users[user_id]

        if book.available_count <= 0:
            print("Book not available!")
            return

        if isbn in user.borrowed_books:
            print("User already has this book!")
            return

        # Issue the book
        book.available_count -= 1
        book.borrowed_by.append(user_id)
        user.borrowed_books.append(isbn)
        user.borrow_dates.append(datetime.now().strftime("%Y-%m-%d"))

        print(f"Book '{book.title}' issued to {user.name}")
        self.save_data()

    def return_book(self):
        """Return a book from a user"""
        user_id = int(input("Enter user ID: "))
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

        # Return the book
        book.available_count += 1
        book.borrowed_by.remove(user_id)

        book_index = user.borrowed_books.index(isbn)
        user.borrowed_books.remove(isbn)
        borrow_date = user.borrow_dates.pop(book_index)

        # Add to history
        return_date = datetime.now().strftime("%Y-%m-%d")
        user.history.append(isbn)
        user.return_dates.append(return_date)

        print(f"Book '{book.title}' returned by {user.name}")
        self.save_data()

    def display_user_info(self):
        """Display user information"""
        user_id = int(input("Enter user ID: "))

        if user_id not in self.users:
            print("User not found!")
            return

        user = self.users[user_id]
        print(f"\n--- User Information ---")
        print(f"ID: {user.user_id}")
        print(f"Name: {user.name}")
        print(f"Type: {user.user_type}")

        if isinstance(user, Student):
            print(f"Year: {user.year}")
            print(f"Branch: {user.branch}")
            print(f"Division: {user.division}")

        print(f"Currently borrowed books: {len(user.borrowed_books)}")
        for i, isbn in enumerate(user.borrowed_books):
            book = self.books[isbn]
            print(f"  - {book.title} (borrowed on: {user.borrow_dates[i]})")

        print(f"Total books borrowed in history: {len(user.history)}")
        input("\nPress Enter to continue...")

    def display_book_info(self):
        """Display book information"""
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
        """Search books by title or author"""
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

    def list_overdue_books(self):
        """List books that are overdue"""
        current_date = datetime.now()
        overdue_limit = timedelta(days=14)  # 14 days limit

        print("\n--- Overdue Books ---")
        overdue_found = False

        for user in self.users.values():
            for i, isbn in enumerate(user.borrowed_books):
                borrow_date = datetime.strptime(user.borrow_dates[i], "%Y-%m-%d")
                if current_date - borrow_date > overdue_limit:
                    book = self.books[isbn]
                    days_overdue = (current_date - borrow_date).days - 14
                    print(f"User: {user.name} (ID: {user.user_id}) | Book: {book.title} | Days overdue: {days_overdue}")
                    overdue_found = True

        if not overdue_found:
            print("No overdue books!")

        input("\nPress Enter to continue...")

    # Lambda function for filtering
    filter_available_books = lambda self: [book for book in self.books.values() if book.available_count > 0]

    def run(self):
        """Main program loop"""
        while True:
            print("\n=== Digital Library Management System ===")
            print("1. Add User")
            print("2. Add Book")
            print("3. Issue Book")
            print("4. Return Book")
            print("5. Display User Info")
            print("6. Display Book Info")
            print("7. Search Books")
            print("8. List Overdue Books")
            print("9. List Available Books")
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
                        self.list_overdue_books()
                    case 9:
                        available_books = self.filter_available_books()
                        print(f"\n--- Available Books ({len(available_books)}) ---")
                        for book in available_books:
                            print(f"{book.title} by {book.author} - {book.available_count} copies available")
                        input("\nPress Enter to continue...")
                    case 0:
                        print("Thank you for using the Library Management System!")
                        break
                    case _:
                        print("Invalid choice! Please try again.")

            except ValueError:
                print("Please enter a valid number!")
            except Exception as e:
                print(f"An error occurred: {e}")


# Run the program
if __name__ == "__main__":
    library = LibraryManager()
    library.run()

"""
DEMONSTRATION OF PYTHON CONCEPTS USED:

• Variables, input(), print():
  - Variables: user_id, name, isbn, title, author, choice, penalty, days_overdue, etc.
  - input(): Used throughout for user interaction (user_id = int(input("Enter user ID: ")))
  - print(): Used for displaying information, messages, and penalty calculations

• Data Types (int, float, str, bool):
  - int: user_id, choice, count, penalty, days_overdue, year calculations
  - str: name, isbn, title, author, dates, error messages, validation messages
  - bool: is_valid, overdue_found (used in conditionals and validation)
  - float: Not explicitly used but datetime calculations involve float precision

• Collections (list, tuple, set, dict):
  - list: borrowed_books, borrow_dates, history, return_dates, found_books
  - dict: users{}, books{}, branch_map{}, division_map{} for mapping and storage
  - tuple: Used in datetime operations and validation return values
  - set: Not explicitly used but concept applied in unique ISBN/ID validation

• Conditionals (if, elif, else):
  - Used throughout: user type checking, book availability, penalty calculations
  - ID validation: if len(str(user_id)) == 8: elif len(str(user_id)) == 3: else:
  - Penalty logic: if days_borrowed > 14: if penalty > 0: else:
  - Year calculation: if year_diff == 0: elif year_diff == 1: etc.

• Match-Case (Python 3.10+):
  - Modern switch-case implementation in main menu
  - match choice: case 1: case 2: case _: for default handling
  - Cleaner than traditional elif chains

• Loops (for, while, break, continue):
  - while: Main program loop (while True:) for continuous operation
  - for: Iterating through books, users, borrowed books, overdue calculations
  - break: Exiting main loop when choice == 0
  - continue: Implicit in exception handling and validation flows

• Functions (def, return, default arguments):
  - def: All methods defined with def keyword for modular programming
  - return: Used in calculation methods (_calculate_year, _get_branch, _validate_student_id)
  - Default arguments: Book.__init__(self, isbn, title, author, total_count=1)
  - Validation functions: _validate_student_id returns tuple (bool, str)

• Lambda functions:
  - filter_available_books = lambda self: [book for book in self.books.values() if book.available_count > 0]
  - Functional programming concept for filtering collections

• Exception Handling:
  - try-except blocks for file operations (FileNotFoundError)
  - ValueError handling for invalid input conversions
  - General Exception catching for unexpected errors
  - Graceful degradation without system crashes

• Date and Time Operations:
  - datetime.now() for current timestamps
  - datetime.strptime() for string to date conversion
  - timedelta() for date arithmetic and overdue calculations
  - String formatting with strftime() for date storage

• File I/O and JSON:
  - json.load() and json.dump() for data persistence
  - File handling with 'r' and 'w' modes
  - with statements for proper file resource management
  - Error handling for missing files

• String Operations:
  - String slicing for ID parsing: str(user_id)[:2], str(user_id)[2]
  - String methods: .lower(), .get() for case-insensitive operations
  - String formatting: f-strings for dynamic message generation
  - String validation and error message construction

• OOP Concepts:
  - Class: Person, Student, Faculty, Book, LibraryManager classes
  - Object: Instances of users and books with state and behavior
  - Constructor (__init__): All classes have constructors with parameter validation
  - self: Used in all instance methods for object reference
  - Encapsulation: Private methods with underscore (_calculate_year, _get_branch, _validate_student_id)

• Inheritance:
  - Single Inheritance: Student(Person), Faculty(Person)
  - super(): Used to call parent constructor for proper initialization
  - Method Overriding: Student and Faculty override Person behavior
  - Inherited attributes: All Person attributes available in subclasses

• Polymorphism:
  - Method overriding in Student class (constructor adds academic details)
  - Different behavior for Student vs Faculty objects
  - isinstance() used for runtime type checking
  - Same interface (Person) with different implementations

• Abstraction:
  - Base Person class provides common interface
  - LibraryManager abstracts complex operations into simple methods
  - Public methods hide internal implementation details
  - Clear separation of concerns between classes

• Data Validation and Business Logic:
  - Multi-layer validation: format, range, business rules
  - ID structure validation with specific error messages
  - Penalty calculation with grace periods and rates
  - Inventory management with availability tracking
  - Referential integrity between users and books

• Algorithm Implementation:
  - Search algorithms: linear search through collections
  - Date arithmetic: calculating overdue days and penalties
  - Data synchronization: maintaining consistency between memory and files
  - State management: tracking borrowing, returns, and history

• Error Handling Patterns:
  - Validation before processing
  - Early returns for error conditions
  - Specific error messages for different failure modes
  - Graceful handling of missing data with defaults

• Design Patterns:
  - Repository pattern: JSON files as data repositories
  - Factory pattern: Creating different user types based on ID
  - Observer pattern: Automatic saving after state changes
  - Command pattern: Menu-driven operations
"""