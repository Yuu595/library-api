import book_repository
import loan_repository
import loan_service
import report_repository
from fines import days_late, fine_for, money


def overdue_report():
    items = []
    total = 0
    for row in report_repository.list_open_loans_with_details():
        fine = fine_for(row["due_date"])
        if fine > 0:
            late_by = days_late(row["due_date"])
            total += fine
            items.append(
                {
                    "loan_id": row["id"],
                    "title": row["title"],
                    "member": row["name"],
                    "days_late": late_by,
                    "fine": money(fine),
                }
            )
    return {"items": items, "total_fines": money(total)}


def summary_report():
    loans = loan_repository.list_loans()
    return {
        "total_books": book_repository.count_books(),
        "on_loan": loan_service.count_open_loans(loans),
        "fines_outstanding": money(loan_service.total_owed(loans)),
    }
