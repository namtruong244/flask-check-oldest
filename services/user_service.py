import flask_bcrypt
from flask_jwt_extended import create_access_token, create_refresh_token

from config.cmn_const import CmnConst
from models.user_model import UserModel


def register_user(request):
    # Check user existed
    user_model = UserModel()
    cursor = user_model.get_user_by_username_and_email(request)
    if cursor.rowcount > 0:
        user = cursor.fetchone()
        message = "Your username is already used by another user"
        if user["EMAIL"] == request["email"]:
            message = "Your email is already used by another user"

        return {"ok": False, "message": message}

    # Generate password hash
    request['password'] = flask_bcrypt.generate_password_hash(request['password'])

    # Start transaction
    user_model.begin()

    data = {
        "USERNAME": request["username"],
        "FULLNAME": request["fullname"],
        "EMAIL": request["email"],
        "PASSWORD": request["password"]
    }

    user_model.insert_data(data)

    user_model.commit()

    return {"ok": True, "message": "User created successfully!"}


def auth_user(request):
    user_model = UserModel()
    column = ["USERNAME", "FULLNAME", "EMAIL", "PASSWORD"]
    condition = {"USERNAME": request["username"], "DELETE_FLG": CmnConst.DELETE_FLG_OFF}
    cursor = user_model.select_data(column, condition)
    if cursor.rowcount == 0:
        return {"ok": False, "message": "Invalid username or password"}

    user = cursor.fetchone()
    if user and flask_bcrypt.check_password_hash(user["PASSWORD"], request["password"]):
        identity = {
            "username": user["USERNAME"],
            "fullname": user["FULLNAME"],
            "email": user["EMAIL"]
        }
        access_token = create_access_token(identity=identity)
        identity["token"] = access_token

        # TODO Improvement refresh_token later
        # refresh_token = create_refresh_token(identity=identity)
        # identity["refresh"] = refresh_token

        return {"ok": True, "data": identity}

    return {"ok": False, "message": "Invalid username or password"}
