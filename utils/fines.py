from datetime import date


FINE_PER_DAY = 0.50


def calculate_fine(days_overdue):
    return max(0, days_overdue) * FINE_PER_DAY


def days_late(due_date):
    return (date.today() - date.fromisoformat(due_date)).days


def fine_for(due_date):
    return calculate_fine(days_late(due_date))


def money(amount):
    return round(float(amount), 2)
