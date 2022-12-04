from config.cmn_const import CmnConst
from models.cmn_model import CmnModel


class UserModel(CmnModel):

    def get_table(self):
        return "USER"

    def get_user_by_username_and_email(self, request):
        sql = (
            "SELECT "
            "  USER_ID, "
            "  USERNAME, "
            "  EMAIL "
            "FROM "
            "  USER "
            "WHERE "
            "  ( "
            "    USERNAME = %s OR "
            "    EMAIL = %s "
            "  ) AND "
            "  DELETE_FLG = %s"
        )

        params = [
            request["username"],
            request["email"],
            CmnConst.DELETE_FLG_OFF
        ]

        return self.query(sql, params)
