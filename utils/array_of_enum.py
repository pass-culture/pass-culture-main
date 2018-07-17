import re

from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.sql.expression import cast


# from http://docs.sqlalchemy.org/en/latest/dialects/postgresql.html#postgresql-array-of-enum


class ArrayOfEnum(ARRAY):

    def bind_expression(self, bindvalue):
        return cast(bindvalue, self)

    def result_processor(self, dialect, coltype):
        super_rp = super(ArrayOfEnum, self).result_processor(
            dialect, coltype)

        def handle_raw_string(value):
            inner = re.match(r"^{(.*)}$", value).group(1)
            return inner.split(",") if inner else []

        def process(value):
            if value is None:
                return None
            return super_rp(handle_raw_string(value))
        return process
