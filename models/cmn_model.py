import logging
import os
import sys
from abc import ABC, abstractmethod

import pymysql
from flask import g
from pymysql.cursors import DictCursor

from exceptions.db_exception import DbException


class CmnModel(ABC):

    @abstractmethod
    def get_table(self):
        pass

    @staticmethod
    def connect():
        try:
            g._curr_db = pymysql.connect(host=os.getenv('MYSQL_HOST'),
                                         user=os.getenv('MYSQL_USER'),
                                         password=os.getenv('MYSQL_PASSWORD'),
                                         database=os.getenv('MYSQL_DB'),
                                         port=int(os.getenv('MYSQL_PORT')),
                                         cursorclass=DictCursor)
        except Exception:
            raise DbException

    @staticmethod
    def close():
        if '_curr_db' in g:
            g._curr_db.close()

    def begin(self):
        g._curr_db.begin()

    def commit(self):
        g._curr_db.commit()

    def rollback(self):
        g._curr_db.rollback()

    def query(self, sql: str, params: (tuple, list)):
        logging.info(sys._getframe().f_code.co_name)
        try:
            with g._curr_db.cursor() as cursor:
                if '%s' in sql:
                    cursor.execute(sql, params)
                else:
                    cursor.execute(sql)
                logging.info(cursor._last_executed)
        except pymysql.Error as e:
            logging.error(e.args[0])
            raise DbException(e)
        return cursor

    def select_data(self, column: list, condition: dict):
        logging.info(sys._getframe().f_code.co_name)
        sql = f"SELECT {', '.join(column)} FROM {self.get_table()}"
        sql_condition = self.get_sql_condition(condition)

        sql += sql_condition['sql']
        return self.query(sql, tuple(sql_condition['params']))

    def insert_data(self, data: dict):
        logging.info(sys._getframe().f_code.co_name)

        sql = f"INSERT INTO {self.get_table()} "
        column, value, params = [], [], []
        for key, val in data.items():
            column.append(f"`{key}`")
            value.append("%s")
            params.append(val)

        column.append("CREATE_DATETIME")
        column.append("UPDATE_DATETIME")
        value.append("NOW()")
        value.append("NOW()")
        sql += f"({','.join(column)}) VALUES ({','.join(value)})"
        return self.query(sql, params)

    def get_sql_condition(self, condition: dict):
        where, params = [], []
        for key, val in condition.items():
            if val is None:
                where.append(key + ' IS NULL')
            elif val == 'IS NOT NULL':
                where.append(key + ' IS NOT NULL')
            elif isinstance(val, list) is True:
                data_in = []
                for v in val:
                    data_in.append('%s')
                    params.append(v)
                where.append(f'{key} IN ({",".join(data_in)})')
            else:
                where.append(f'{key} = %s')
                params.append(val)
        sql = ' WHERE ' + ' AND '.join(where)
        return {'sql': sql, 'params': params}
