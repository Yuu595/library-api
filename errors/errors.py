from flask import jsonify


def error_response(message, status):
    return jsonify({"error": message}), status
