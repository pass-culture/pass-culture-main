from pcapi.connectors.dms import exceptions as dms_exceptions


class DmsGraphQLApiErrorTest:
    def test_is_not_found(self):
        error = dms_exceptions.DmsGraphQLApiError(
            [
                {
                    "message": "DossierClasserSansSuitePayload not found",
                    "locations": [{"line": 2, "column": 3}],
                    "path": ["dossierClasserSansSuite"],
                    "extensions": {"code": "not_found"},
                }
            ]
        )
        assert error.is_not_found

    def test_other(self):
        error = dms_exceptions.DmsGraphQLApiError(
            [
                {
                    "message": "DossierClasserSansSuitePayload not found",
                    "locations": [{"line": 2, "column": 3}],
                    "path": ["dossierClasserSansSuite"],
                    "extensions": {"code": "something"},
                }
            ]
        )
        assert not error.is_not_found
