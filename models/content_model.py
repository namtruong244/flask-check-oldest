from models.cmn_model import CmnModel
from config.cmn_const import CmnConst


class ContentModel(CmnModel):

    def get_table(self):
        return "CONTENT"

    def get_all_content(self):
        sql = (
            "SELECT "
            "  ct.ID, "
            "  ct.USER_ID, "
            "  u.USERNAME, "
            "  u.FULLNAME, "
            "  u.EMAIL, "
            "  ct.CONTENT, "
            "  ct.CLASS_TYPE, "
            "  ct.LANGUAGE_TYPE, "
            "  ct.TITLE "
            "FROM "
            "  CONTENT AS ct "
            "  INNER JOIN USER as u ON "
            "    ct.USER_ID = u.USER_ID AND "
            "    ct.DELETE_FLG = %s AND "
            "    u.DELETE_FLG = %s "
        )

        params = [
            CmnConst.DELETE_FLG_OFF,
            CmnConst.DELETE_FLG_OFF
        ]

        return self.query(sql, params)
