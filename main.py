import datetime
import logging
import os
import traceback

from dotenv import load_dotenv
from flask import Flask, request
from flask_jwt_extended import JWTManager, jwt_required, get_jwt_identity
from flask_bcrypt import Bcrypt
from flask_cors import CORS

from exceptions.cmn_error import CmnError
from models.cmn_model import CmnModel
from schemas.content_schema import validate_content
from schemas.user_schema import validate_user
from services import user_service, content_service
from utils.util import CmnUtil
from werkzeug.utils import secure_filename
from config.cmn_const import CmnConst
import uuid

load_dotenv()


# create the flask object
app = Flask(__name__)

CORS(app)

app.config["JWT_SECRET_KEY"] = "c6e1cfc4e90bb9e71da16bc217017b87b0eedd3c3ffdde0e2d777ddca0a88597"
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = datetime.timedelta(days=5)
app.config["JSON_SORT_KEYS"] = False
app.config['UPLOAD_FOLDER'] = CmnConst.UPLOAD_FOLDER
app.config['CORS_HEADERS'] = 'Content-Type'


# Port variable to run the server on.
PORT = os.environ.get("PORT")

flask_bcrypt = Bcrypt(app)
jwt = JWTManager(app)


@app.before_request
def before_request_handler():
    """ Connect to DB before execute """
    CmnModel.connect()


@app.errorhandler(404)
def not_found_error_handler(error):
    """ 404 error handler """
    logging.error(error)
    return CmnUtil.response_error("URL was not found on the server", http_status_code=404)


@app.errorhandler(Exception)
def exception(error):
    """ error handler """
    logging.error(traceback.format_exc())
    return CmnError.handle_exception(error)


@jwt.unauthorized_loader
def unauthorized_response(callback):
    return CmnUtil.response_error("Missing Authorization Header", http_status_code=401)


@app.route("/api/user/register", methods=["POST"])
def register_user():
    """ Register user endpoint """

    # Validate request data
    data = validate_user(request.get_json(), "register")
    if data["ok"] is False:
        return CmnUtil.response_error("Bad request parameters: {}".format(data["message"]))

    result = user_service.register_user(data["data"])
    if result["ok"] is False:
        return CmnUtil.response_error(result["message"], http_status_code=400)

    return CmnUtil.response_success_create(result["message"])


@app.route("/api/user/auth", methods=["POST"])
def auth_user():
    """ Auth endpoint """

    # Validate request data
    data = validate_user(request.get_json(), "auth")
    if data["ok"] is False:
        return CmnUtil.response_error("Bad request parameters: {}".format(data["message"]))

    result = user_service.auth_user(data["data"])
    if result["ok"] is False:
        return CmnUtil.response_error(result["message"], http_status_code=400)

    return CmnUtil.response_success(result["data"])


@app.route("/api/content", methods=["GET"])
@jwt_required()
def get_all_content():
    """ Get all content endpoint """

    return CmnUtil.response_success(content_service.get_all_content())


@app.route("/api/content", methods=["POST"])
@jwt_required()
def create_content():
    """ Create content endpoint """

    # Validate request data
    data = validate_content(request.get_json())
    if data["ok"] is False:
        return CmnUtil.response_error("Bad request parameters: {}".format(data["message"]))

    current_user = get_jwt_identity()
    result = content_service.create_new_content(data["data"], current_user)
    if result["ok"] is False:
        return CmnUtil.response_error(result["message"], http_status_code=400)

    return CmnUtil.response_success_create(result["message"])


@app.route("/api/content", methods=["PUT"])
@jwt_required()
def update_content():
    """ Update content endpoint """

    # Validate request data
    data = validate_content(request.get_json())
    # TODO


@app.route("/api/speech-recognizer", methods=["POST"])
@jwt_required()
def speech_recognizer_to_text():
    """ Speech recognizer to text """

    if "file" not in request.files:
        return CmnUtil.response_error("No file part", 404)
    file = request.files["file"]

    if file.filename == "":
        return CmnUtil.response_error("No selected file", 404)

    if file and CmnUtil.check_allowed_file(file.filename):
        file_name = str(uuid.uuid4())
        file_name_with_extension = file_name + ".wav"
        path_file = os.path.join(app.config["UPLOAD_FOLDER"], file_name_with_extension)
        file.save(path_file)
        result = content_service.get_text_from_speech(file_name, dict(request.values))
        os.remove(path_file)

        if result["ok"] is False:
            return CmnUtil.response_error(result["message"], http_status_code=200)

        return CmnUtil.response_success(result["text"])

    return CmnUtil.response_error("File is not allowed", http_status_code=400)


@app.route("/api/content/test", methods=["POST"])
def test_content():
    """ Test content endpoint """

    result = content_service.compare_text_result(request.get_json())
    if result["ok"] is False:
        return CmnUtil.response_error(result["message"])

    return CmnUtil.response_success(result["data"])


if __name__ == "__main__":
    logging.info("running environment: %s", os.environ.get("ENV"))
    app.config["DEBUG"] = os.environ.get("ENV") == "development"  # Debug mode if development env
    app.run(port=os.getenv("PORT", default=5000))
