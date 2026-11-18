import os

from flask import Flask

from routes import book_routes, loan_routes, member_routes, report_routes
from db import init_db
from errors import LibraryError, error_response

app = Flask(__name__)
app.register_blueprint(book_routes.bp)
app.register_blueprint(member_routes.bp)
app.register_blueprint(loan_routes.bp)
app.register_blueprint(report_routes.bp)


@app.errorhandler(LibraryError)
def handle_library_error(error):
    return error_response(error.message, error.status)


if not os.path.exists("library.db"):
    init_db()
