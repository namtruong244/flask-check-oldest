import pymysql
from flask import g
from exceptions.db_exception import DbException
from utils.util import CmnUtil


class CmnError:
    @staticmethod
    def handle_exception(e):
        message = "System Error"

        # database exception
        if isinstance(e, DbException) or isinstance(e, pymysql.Error):
            message = "DB Error"

        if '_curr_db' in g:
            g._curr_db.rollback()
            g._curr_db.close()

        return CmnUtil.response_error(message, http_status_code=500)
