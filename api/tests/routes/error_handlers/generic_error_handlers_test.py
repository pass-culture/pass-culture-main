from datetime import datetime


class FormatQueryParamsTest:
    def test_format_params(self, app):
        with app.app_context():
            from pcapi.routes.error_handlers.utils import format_sql_statement_params
        sqla_params = {
            "token_1": "E3PGVS",
            "lower_1": "pctest.jeune93.has-booked-some.v1@example.com",
            "id_1": 270,
            "date_1": datetime(2021, 1, 1, 12, 0, 10),
            "list_1": [datetime(2021, 1, 1), 270, "E3PGVS"],
        }

        formatted_pararms = format_sql_statement_params(sqla_params)

        assert formatted_pararms == {
            "token_1": "'E3PGVS'",
            "lower_1": "'pctest.jeune93.has-booked-some.v1@example.com'",
            "id_1": 270,
            "date_1": "'2021-01-01 12:00:10'",
            "list_1": ["'2021-01-01 00:00:00'", 270, "'E3PGVS'"],
        }
