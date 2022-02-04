import collections
import datetime
import logging
import typing

import pydantic

# pas nécessaire sur les environnements, seulement en local
# import os
# os.environ.setdefault("CORS_ALLOWED_ORIGINS", "*")
# os.environ.setdefault("CORS_ALLOWED_ORIGINS_NATIVE", "*")
# os.environ.setdefault("CORS_ALLOWED_ORIGINS_ADAGE_IFRAME", "*")
# os.environ.setdefault("DEMARCHES_SIMPLIFIEES_ENROLLMENT_PROCEDURE_ID_v2", "0")
# os.environ.setdefault("DEMARCHES_SIMPLIFIEES_ENROLLMENT_PROCEDURE_ID_v3", "0")
# os.environ.setdefault("JWT_SECRET_KEY", "fépachié")
# os.environ.setdefault("DATABASE_URL", "postgresql://pass_culture:passq@localhost:5434/pass_culture")


from pcapi.core.mails.models.models import Email
from pcapi.core.offers.models import Offer
from pcapi.core.offers.models import OfferValidationConfig
from pcapi.flask_app import app
from pcapi.models import db
from pcapi.models.product import Product


app.app_context().push()


LOGGER = logging.getLogger("__name__")
BATCH_SIZE = 1000  # number of rows to update in one query
TABLE_UPDATE_QUERY_FORMAT = (
    'WITH converted(id, "{jsonb_field}") AS ('
    '    SELECT id, "{json_field}"::JSONB AS "{jsonb_field}" '
    '    FROM {table} '
    '    WHERE "{json_field}" IS NOT NULL AND "{jsonb_field}" IS NULL '
    '    LIMIT {limit}'
    ') '
    'UPDATE {table} '
    'SET "{jsonb_field}" = converted."{jsonb_field}" '
    'FROM converted '
    'WHERE {table}.id = converted.id '
    'RETURNING {table}.id'
)


class TableData(pydantic.BaseModel):
    name: str
    json_field: str
    jsonb_field: str

    def __hash__(self):
        return hash((self.name, self.json_field, self.jsonb_field))


class MigrationSession(pydantic.BaseModel):
    rows_processed: int
    time_spent: datetime.timedelta

    def __bool__(self):
        return bool(self.rows_processed)


class TableMigrationSession(pydantic.BaseModel):
    table: TableData
    migration: MigrationSession


TO_BE_POPULATED = [
    TableData(name=Email.__tablename__, json_field='content',  jsonb_field='contentNew'),
    TableData(name=OfferValidationConfig.__tablename__, json_field='specs',  jsonb_field='specsNew'),
    TableData(name=Product.__tablename__, json_field='extraData',  jsonb_field='jsonData'),
    TableData(name=Offer.__tablename__, json_field='extraData',  jsonb_field='jsonData'),
]


def populate_batch(table_data: TableData, batch_size: int) -> MigrationSession:
    start_time = datetime.datetime.now()
    query = TABLE_UPDATE_QUERY_FORMAT.format(
        table=table_data.name,
        json_field=table_data.json_field,
        jsonb_field=table_data.jsonb_field,
        limit=batch_size,
    )
    result = db.session.execute(query)
    db.session.execute("COMMIT;")
    return MigrationSession(rows_processed=result.rowcount, time_spent=datetime.datetime.now() - start_time)


def populate_model(table_data: TableData) -> typing.Union[MigrationSession, bool]:
    stop = False
    start_time = datetime.datetime.now()
    model_session = MigrationSession(rows_processed=0, time_spent=datetime.timedelta())
    LOGGER.info(f"migrating {table_data.name} [{table_data.json_field} -> {table_data.jsonb_field}]")

    try:
        while batch_session := populate_batch(table_data, BATCH_SIZE):
            model_session.rows_processed += batch_session.rows_processed
            model_session.time_spent = datetime.datetime.now() - start_time
            LOGGER.info(
                f"\t{batch_session.rows_processed} rows processed in {batch_session.time_spent} "
                f"(total: {model_session.rows_processed} in {model_session.time_spent})"
            )
        else:
            LOGGER.info("\tno more row need to be migrated")

    except KeyboardInterrupt:
        stop = True

    return model_session, stop


def main():
    session_data = collections.defaultdict(MigrationSession)
    start_time = datetime.datetime.now()
    for table_data in TO_BE_POPULATED:
        table_session, stop = populate_model(table_data=table_data)
        session_data[table_data] = table_session
        if stop:
            break

    LOGGER.info(
        '\n'.join([f"Session summary (total time: {datetime.datetime.now() - start_time}):"] + [
            f"- migrated data from {table.json_field} to {table.jsonb_field} "
            f"on {session.rows_processed} {table.name} rows in {session.time_spent}"
            for table, session in session_data.items()
        ])
    )


if __name__ == "__main__":
    main()
