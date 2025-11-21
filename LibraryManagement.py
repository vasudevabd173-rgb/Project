import sqlite3
from datetime import datetime, timedelta

# ======================================================
#                 DATABASE & TABLES
# ======================================================

conn = sqlite3.connect('Library.db')
cursor = conn.cursor()

cursor.execute('''
CREATE TABLE IF NOT EXISTS User(
user_id INTEGER PRIMARY KEY AUTOINCREMENT,
name VARCHAR(20) NOT NULL,
email TEXT UNIQUE NOT NULL,
password TEXT NOT NULL,
phone INTEGER,
address TEXT,
join_date DATE DEFAULT(DATE('now')),
role TEXT DEFAULT 'User')
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS Book(
book_id INTEGER PRIMARY KEY AUTOINCREMENT,
title VARCHAR(20) NOT NULL,
author VARCHAR(20) NOT NULL,
category VARCHAR(20),
total_copies INTEGER DEFAULT 1,
available_copies INTEGER DEFAULT 1
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS Borrow(
borrow_id INTEGER PRIMARY KEY AUTOINCREMENT,
user_id INTEGER,
book_id INTEGER,
borrow_date DATE DEFAULT(DATE('now')),
due_date DATE NOT NULL,
return_date DATE,
status TEXT DEFAULT 'Borrowed',
FOREIGN KEY(user_id) REFERENCES User(user_id),
FOREIGN KEY(book_id) REFERENCES Book(book_id))
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS Fine(
fine_id INTEGER PRIMARY KEY AUTOINCREMENT,
borrow_id INTEGER,
user_id INTEGER,
late_days INTEGER,
fine_amount INTEGER,
status TEXT DEFAULT 'Unpaid',
FOREIGN KEY(borrow_id) REFERENCES Borrow(borrow_id),
FOREIGN KEY(user_id) REFERENCES User(user_id))
''')

conn.commit()

# ======================================================
#                 USER FUNCTIONS
# ======================================================

def register_user():
    conn = sqlite3.connect('Library.db')
    cursor = conn.cursor()

    print("\n----- Register New User -----")
    name = input("Enter Name: ")
    email = input("Email: ")
    password = input("Password: ")
    phone = input("Phone: ")

    try:
        cursor.execute('''
        INSERT INTO User(name,email,password,phone,role)
        VALUES(?,?,?,?,'User')
        ''', (name, email, password, phone))

        conn.commit()
        print("✅ Registration Successful")

    except sqlite3.IntegrityError:
        print("❌ User Already Exists")
    conn.close()


def login_user():
    conn = sqlite3.connect("Library.db")
    cursor = conn.cursor()

    print("\n----- Login -----")
    email = input("Email: ")
    password = input("Password: ")

    cursor.execute(
        "SELECT user_id, name, role FROM User WHERE email=? AND password=?",
        (email, password),
    )

    user = cursor.fetchone()
    conn.close()

    if user:
        print(f"✅ Welcome {user[1]} ({user[2]})")
        return user
    else:
        print("❌ Invalid Email or Password")
        return None


def update_password(user_id):
    conn = sqlite3.connect("Library.db")
    cursor = conn.cursor()

    print("\n--- Update Password ---")
    old = input("Enter Old Password: ")

    cursor.execute("SELECT password FROM User WHERE user_id=?", (user_id,))
    current = cursor.fetchone()

    if old != current[0]:
        print("❌ Wrong Old Password")
        return

    new = input("Enter New Password: ")
    confirm = input("Confirm New Password: ")

    if new != confirm:
        print("❌ Passwords Do Not Match")
        return

    cursor.execute("UPDATE User SET password=? WHERE user_id=?", (new, user_id))
    conn.commit()
    print("✅ Password Updated")


# ======================================================
#             DEFAULT LIBRARIAN CREATION
# ======================================================

def create_librarian_account():
    conn = sqlite3.connect("Library.db")
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM User WHERE role='Librarian'")
    exists = cursor.fetchone()

    if not exists:
        cursor.execute('''
        INSERT INTO User(name,email,password,role)
        VALUES('Admin','admin','admin','Librarian')
        ''')
        conn.commit()
        print("📌 Default Librarian Created (Email: admin, Pass: admin)")

    conn.close()


# ======================================================
#                 LIBRARIAN FUNCTIONS
# ======================================================

def view_all_users():
    conn = sqlite3.connect("Library.db")
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM User")
    users = cursor.fetchall()

    if not users:
        print("\nNo Users Found")
        return

    print("\n----- All Users -----")
    for u in users:
        print(f"""
User ID : {u[0]}
Name    : {u[1]}
Email   : {u[2]}
Phone   : {u[4]}
Role    : {u[7]}
--------------------------------
""")


# ======================================================
#                 BOOK FUNCTIONS
# ======================================================

def add_book():
    conn = sqlite3.connect("Library.db")
    cursor = conn.cursor()

    print("\n--- Add Book ---")
    title = input("Title: ")
    author = input("Author: ")
    category = input("Category: ")
    copies = int(input("Total Copies: "))

    cursor.execute("""
    INSERT INTO Book(title,author,category,total_copies,available_copies)
    VALUES(?,?,?,?,?)
    """, (title, author, category, copies, copies))

    conn.commit()
    conn.close()
    print("✅ Book Added Successfully")


def view_books():
    conn = sqlite3.connect("Library.db")
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM Book")
    books = cursor.fetchall()

    print("\n----- Available Books -----")
    print('\nBook ID | Title | Author |\n ')
    for b in books:
        print(f"{b[0]} | {b[1]} | {b[2]} | {b[5]} copies")
    conn.close()


# ---------------- SEARCH SYSTEM ----------------

def search_books():
    conn = sqlite3.connect("Library.db")
    cursor = conn.cursor()

    print("""
    ----- Search Book -----
    1. Search by Title
    2. Search by Author
    3. Search by Category
    4. Search by Book ID
    """)
    choice = input("Enter Choice: ")

    if choice == "1":
        key = input("Enter Title: ")
        cursor.execute("SELECT * FROM Book WHERE title LIKE ?", ("%" + key + "%",))

    elif choice == "2":
        key = input("Enter Author: ")
        cursor.execute("SELECT * FROM Book WHERE author LIKE ?", ("%" + key + "%",))

    elif choice == "3":
        key = input("Enter Category: ")
        cursor.execute("SELECT * FROM Book WHERE category LIKE ?", ("%" + key + "%",))

    elif choice == "4":
        key = int(input("Enter Book ID: "))
        cursor.execute("SELECT * FROM Book WHERE book_id=?", (key,))

    else:
        print("❌ Invalid Choice")
        return

    results = cursor.fetchall()
    conn.close()

    if not results:
        print("❌ No Books Found")
    else:
        print("\n----- Search Results -----")
        for b in results:
            print(f"{b[0]} | {b[1]} | {b[2]} | {b[5]} copies")


def edit_book_details():
    conn = sqlite3.connect("library.db")
    cursor = conn.cursor()

    book_id = input("Enter Book ID to edit: ")

    cursor.execute("SELECT * FROM books WHERE book_id = ?", (book_id,))
    book = cursor.fetchone()

    if not book:
        print("❌ No book found with this ID.")
        conn.close()
        return

    print("\n--- Current Book Details ---")
    print(f"1. Title    : {book[1]}")
    print(f"2. Author   : {book[2]}")
    print(f"3. Quantity : {book[3]}")
    print("-----------------------------")

    print("\nWhat do you want to update?")
    print("1. Edit Title")
    print("2. Edit Author")
    print("3. Edit Quantity")
    print("4. Edit All")
    choice = input("Enter choice: ")

    if choice == "1":
        new_title = input("Enter new title: ")
        cursor.execute("UPDATE books SET title = ? WHERE book_id = ?", (new_title, book_id))
        print("✔ Title updated.")

    elif choice == "2":
        new_author = input("Enter new author: ")
        cursor.execute("UPDATE books SET author = ? WHERE book_id = ?", (new_author, book_id))
        print("✔ Author updated.")

    elif choice == "3":
        new_qty = input("Enter new quantity: ")
        cursor.execute("UPDATE books SET quantity = ? WHERE book_id = ?", (new_qty, book_id))
        print("✔ Quantity updated.")

    elif choice == "4":
        new_title = input("Enter new title: ")
        new_author = input("Enter new author: ")
        new_qty = input("Enter new quantity: ")

        cursor.execute("""
            UPDATE books 
            SET title = ?, author = ?, quantity = ?
            WHERE book_id = ?
        """, (new_title, new_author, new_qty, book_id))

        print("✔ All details updated successfully.")

    else:
        print("❌ Invalid choice")

    conn.commit()
    conn.close()


def delete_book():
    conn = sqlite3.connect("Library.db")
    cursor = conn.cursor()

    book_id = int(input("Enter Book ID to delete: "))

    cursor.execute("DELETE FROM Book WHERE book_id=?", (book_id,))
    conn.commit()
    print("✅ Book Deleted")


# ======================================================
#                BORROW FUNCTIONS
# ======================================================

def borrow_book(user_id):
    conn = sqlite3.connect("Library.db")
    cursor = conn.cursor()

    book_id = int(input("\nEnter Book ID: "))

    cursor.execute("SELECT available_copies FROM Book WHERE book_id=?", (book_id,))
    book = cursor.fetchone()

    if book and book[0] > 0:
        due_date = (datetime.now() + timedelta(days=4)).date()

        cursor.execute("""
        INSERT INTO Borrow(user_id,book_id,due_date)
        VALUES(?,?,?)
        """, (user_id, book_id, due_date))

        cursor.execute("""
        UPDATE Book SET available_copies=available_copies-1 WHERE book_id=?
        """, (book_id,))

        conn.commit()
        print("✅ Book Borrowed Successfully")

    else:
        print("❌ Book Not Available")
    conn.close()


def return_book(user_id):
    conn = sqlite3.connect("Library.db")
    cursor = conn.cursor()

    borrow_id = int(input("Enter Borrow ID: "))

    cursor.execute("""
    SELECT book_id, due_date FROM Borrow
    WHERE borrow_id=? AND user_id=? AND status='Borrowed'
    """, (borrow_id, user_id))

    record = cursor.fetchone()

    if not record:
        print("❌ Invalid Borrow ID")
        return

    book_id, due = record
    due_date = datetime.strptime(due, "%Y-%m-%d").date()
    today = datetime.now().date()

    cursor.execute("""
    UPDATE Borrow SET status='Returned',return_date=DATE('now') WHERE borrow_id=?
    """, (borrow_id,))

    cursor.execute("""
    UPDATE Book SET available_copies=available_copies+1 WHERE book_id=?
    """, (book_id,))

    conn.commit()
    print("✅ Book Returned")

    # FINE CALCULATION
    late_days = (today - due_date).days

    if late_days > 0:
        fine_amt = late_days * 50

        cursor.execute("""
        INSERT INTO Fine(borrow_id,user_id,late_days,fine_amount)
        VALUES(?,?,?,?)
        """, (borrow_id, user_id, late_days, fine_amt))

        conn.commit()
        print(f"⚠ Late by {late_days} days — Fine Added: ₹{fine_amt}")

    conn.close()



def view_all_borrow_records():
    conn = sqlite3.connect("library.db")
    cursor = conn.cursor()

    # Fetch all borrow records
    cursor.execute("SELECT * FROM Borrow ORDER BY borrow_id DESC")
    borrow_records = cursor.fetchall()

    if not borrow_records:
        print("\nNo borrow records found.")
        conn.close()
        return

    print("\n===== ALL BORROW RECORDS =====")

    for record in borrow_records:
        borrow_id = record[0]
        user_id = record[1]
        book_id = record[2]
        borrow_date = record[3]
        due_date = record[4]
        return_date = record[5]
        fine = record[6]

        # Get username from users table
        cursor.execute("SELECT name FROM User WHERE user_id = ?", (user_id,))
        user = cursor.fetchone()
        username = user[0] if user else "Unknown User"

        # Get book title from books table
        cursor.execute("SELECT title FROM Book WHERE book_id = ?", (book_id,))
        book = cursor.fetchone()
        book_title = book[0] if book else "Unknown Book"

        print(f"""
Borrow ID     : {borrow_id}
User          : {username}
Book          : {book_title}
Borrow Date   : {borrow_date}
Due Date      : {due_date}
Return Date   : {return_date}
Fine (Rs)     : {fine}
-----------------------------------------
""")




def view_user_borrow_history(user_id):
    conn = sqlite3.connect("Library.db")
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM Borrow WHERE user_id=?", (user_id,))
    rows = cursor.fetchall()

    print("\n----- Your Borrow History -----")
    for r in rows:
        print(f"Borrow ID: {r[0]} | Book ID: {r[2]} | Status: {r[6]}")

    conn.close()


# ======================================================
#                    FINES
# ======================================================

def view_user_fines(user_id):
    conn = sqlite3.connect("Library.db")
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM Fine WHERE user_id=?", (user_id,))
    fines = cursor.fetchall()

    if not fines:
        print("\n🎉 You have no fines!")
        return

    print("\n----- Your Fines -----")
    for f in fines:
        print(f"Fine ID: {f[0]} | Borrow ID: {f[1]} | Amount: ₹{f[4]} | Status: {f[5]}")

    conn.close()


def view_all_fines():
    conn = sqlite3.connect("Library.db")
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM Fine")
    fines = cursor.fetchall()

    print("\n----- All Fines -----")
    for f in fines:
        print(f"Fine ID: {f[0]} | User ID: {f[2]} | Amount: ₹{f[4]} | Status: {f[5]}")


# ======================================================
#                    MENUS
# ======================================================

def librarian_menu(user):
    while True:
        print("""
==========================
      LIBRARIAN MENU
==========================
1. View All Users
2. Add Book
3. View Books
4. Search Book
5. Delete Book
6. View All Borrow Records
7. View All Fines
8. Logout
""")
        choice = input("Enter Choice: ")

        if choice == "1":
            view_all_users()
        elif choice == "2":
            add_book()
        elif choice == "3":
            view_books()
        elif choice == "4":
            search_books()
        elif choice == "5":
            delete_book()
        elif choice == "6":
            view_all_borrow_records()
        elif choice == "7":
            view_all_fines()
        elif choice == "8":
            break
        else:
            print("❌ Invalid Choice")


def user_menu(user):
    user_id = user[0]

    while True:
        print(f"""
==========================
        USER MENU
==========================
1. View Books
2. Search Books
3. Borrow Book
4. Return Book
5. My Borrow History
6. My Fines
7. Update Password
8. Logout
""")
        choice = input("Enter Choice: ")

        if choice == "1":
            view_books()
        elif choice == "2":
            search_books()
        elif choice == "3":
            borrow_book(user_id)
        elif choice == "4":
            return_book(user_id)
        elif choice == "5":
            view_user_borrow_history(user_id)
        elif choice == "6":
            view_user_fines(user_id)
        elif choice == "7":
            update_password(user_id)
        elif choice == "8":
            break
        else:
            print("❌ Invalid Choice")


# ======================================================
#                  MAIN MENU
# ======================================================

def main_menu():
    create_librarian_account()

    while True:
        print("""
==========================
        MAIN MENU
==========================
1. Register
2. Login
3. Exit
""")
        choice = input("Enter Choice: ")

        if choice == "1":
            register_user()
        elif choice == "2":
            user = login_user()
            if user:
                if user[2] == "Librarian":
                    librarian_menu(user)
                else:
                    user_menu(user)
        elif choice == "3":
            print("Goodbye!")
            break
        else:
            print("❌ Invalid Choice")


main_menu()