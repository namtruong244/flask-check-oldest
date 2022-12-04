from flask import make_response, jsonify
from config.cmn_const import CmnConst


class CmnUtil:

    def __init__(self):
        pass

    @staticmethod
    def response_success(data=None):
        body = {"header": {"error": None, "message": "Process ended normal"}}

        if data is not None:
            body["result"] = data

        return make_response(jsonify(body), 200)

    @staticmethod
    def response_success_create(data=None):
        body = {"header": {"error": None, "message": "Process ended normal"}}

        if data is not None:
            body["result"] = data

        return make_response(jsonify(body), 201)

    @staticmethod
    def response_error(message, data=None, http_status_code=400):
        body = {"header": {"error": True, "message": message}}

        if data is not None:
            body["result"] = data

        return make_response(jsonify(body), http_status_code)

    @staticmethod
    def check_allowed_file(file_name: str):
        return "." in file_name and file_name.rsplit('.', 1)[1].lower() in CmnConst.ALLOWED_FILE_EXTENSIONS
