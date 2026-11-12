import db


def list_books(only_available):
    with db.connection() as conn:
        if only_available:
            return conn.execute("SELECT * FROM books WHERE available = 1").fetchall()
        return conn.execute("SELECT * FROM books").fetchall()


def get_book(book_id):
    with db.connection() as conn:
        return conn.execute("SELECT * FROM books WHERE id = ?", (book_id,)).fetchone()


def create_book(title, author, isbn):
    with db.connection() as conn:
        cur = conn.execute(
            "INSERT INTO books (title, author, isbn, available) VALUES (?, ?, ?, 1)",
            (title, author, isbn),
        )
        conn.commit()
        return conn.execute("SELECT * FROM books WHERE id = ?", (cur.lastrowid,)).fetchone()


def delete_book(book_id):
    with db.connection() as conn:
        conn.execute("DELETE FROM books WHERE id = ?", (book_id,))
        conn.commit()


def count_books():
    with db.connection() as conn:
        return conn.execute("SELECT COUNT(*) FROM books").fetchone()[0]
