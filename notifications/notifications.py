OUTBOX_PATH = "outbox.txt"


def send_due_date_reminder(member, loan):
    print("Due date reminder for " + member["name"] + ": loan due " + loan["due_date"])
    return True


def send_overdue_notice(member, loan):
    print("Overdue notice for " + member["name"] + ": loan " + str(loan["id"]))
    return True


def send_email(email, subject, body):
    with open(OUTBOX_PATH, "a") as outbox:
        outbox.write("TO: " + email + " | SUBJECT: " + subject + " | BODY: " + body + "\n")
