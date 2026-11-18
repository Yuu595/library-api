from datetime import date


STUDENT_LOAN_LIMIT = 3
STAFF_LOAN_LIMIT = 5


def is_book_available(book):
    return book["available"] != 0


def has_unpaid_fines(amount_owed):
    return amount_owed > 0


def has_reached_borrowing_limit(open_loans, member_type):
    limit = STAFF_LOAN_LIMIT if member_type == "staff" else STUDENT_LOAN_LIMIT
    return open_loans >= limit


def is_loan_overdue(loan):
    return loan["returned"] == 0 and date.fromisoformat(loan["due_date"]) < date.today()
