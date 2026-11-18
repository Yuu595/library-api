from datetime import date, timedelta

from repositories import book_repository, loan_repository, member_repository
from notifications import send_due_date_reminder, send_email, send_overdue_notice
from errors import bad_request, conflict, not_found
from utils import checks, validation
from utils.checks import STAFF_LOAN_LIMIT, STUDENT_LOAN_LIMIT
from utils.fines import fine_for, money

LOAN_DURATION_DAYS = 14
MAX_RENEWALS = 1


def amount_owed(loan):
    if loan["returned"] == 0:
        return fine_for(loan["due_date"])
    if loan["fine_paid"] == 0:
        return loan["fine"]
    return 0


def total_owed(loans):
    return sum(amount_owed(loan) for loan in loans)


def count_open_loans(loans):
    return sum(1 for loan in loans if loan["returned"] == 0)


def current_fine(loan):
    if loan["returned"] == 0:
        return fine_for(loan["due_date"])
    return loan["fine"]


def is_overdue(loan):
    return checks.is_loan_overdue(loan)


def list_loans(only_overdue):
    loans = loan_repository.list_loans()
    if only_overdue:
        return [loan for loan in loans if is_overdue(loan)]
    return loans


def get_loan(loan_id):
    loan = loan_repository.get_loan(loan_id)
    if loan is None:
        raise not_found("loan not found")
    return loan


def create_loan(data):
    if not validation.has_required_fields(data, ("book_id", "member_id")):
        raise bad_request("book_id and member_id are required")
    if data.get("due_date") and not validation.is_valid_date(data["due_date"]):
        raise bad_request("invalid due_date")

    book = book_repository.get_book(data["book_id"])
    if book is None:
        raise not_found("book not found")
    member = member_repository.get_member(data["member_id"])
    if member is None:
        raise not_found("member not found")
    if not checks.is_book_available(book):
        raise conflict("book is not available")

    loans = loan_repository.list_loans_for_member(data["member_id"])
    if checks.has_unpaid_fines(total_owed(loans)):
        raise conflict("member has unpaid fines")
    if checks.has_reached_borrowing_limit(count_open_loans(loans), member["type"]):
        raise conflict("loan limit reached")

    today = date.today()
    due_date = data.get("due_date") or (today + timedelta(days=LOAN_DURATION_DAYS)).isoformat()
    loan = loan_repository.create_loan(
        data["book_id"], data["member_id"], due_date, today.isoformat()
    )
    send_due_date_reminder(member, loan)
    send_email(member["email"], "Book checked out", "You checked out " + book["title"])
    return loan


def return_book(loan_id):
    loan = get_loan(loan_id)
    if loan["returned"] == 1:
        raise conflict("loan already returned")

    fine = fine_for(loan["due_date"])
    updated = loan_repository.mark_returned(loan_id, loan["book_id"], fine)
    member = member_repository.get_member(loan["member_id"])
    book = book_repository.get_book(loan["book_id"])
    if fine > 0:
        send_overdue_notice(member, updated)
    send_email(
        member["email"], "Book returned", "You returned " + book["title"] + ". Fine: $" + str(money(fine))
    )
    return updated


def renew_loan(loan_id):
    loan = get_loan(loan_id)
    if loan["returned"] == 1:
        raise conflict("loan already returned")
    if date.fromisoformat(loan["due_date"]) < date.today():
        raise conflict("overdue loans cannot be renewed")
    if loan["renewals"] >= MAX_RENEWALS:
        raise conflict("loan was already renewed")

    new_due_date = (date.fromisoformat(loan["due_date"]) + timedelta(days=LOAN_DURATION_DAYS)).isoformat()
    updated = loan_repository.extend_loan(loan_id, new_due_date)
    member = member_repository.get_member(loan["member_id"])
    book = book_repository.get_book(loan["book_id"])
    send_email(member["email"], "Loan renewed", "You renewed " + book["title"])
    return updated


def pay_fine(loan_id):
    loan = get_loan(loan_id)
    if loan["returned"] == 0:
        raise conflict("return the book before paying")
    if loan["fine"] <= 0 or loan["fine_paid"] == 1:
        raise conflict("no fine to pay")

    updated = loan_repository.mark_fine_paid(loan_id)
    member = member_repository.get_member(loan["member_id"])
    send_email(
        member["email"], "Fine paid", "We received $" + str(money(loan["fine"]))
    )
    return updated
