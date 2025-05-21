import pytest
from werkzeug.exceptions import NotFound

from pcapi.core.chronicles import factories as chronicles_factories
from pcapi.core.chronicles import models as chronicles_models
from pcapi.models import db
from pcapi.routes.backoffice import search_utils


pytestmark = [
    pytest.mark.usefixtures("db_session"),
    pytest.mark.backoffice,
]


class PaginateTest:
    def test_paginate(self):
        chronicles = chronicles_factories.ChronicleFactory.create_batch(7)
        query = db.session.query(chronicles_models.Chronicle.id).order_by(chronicles_models.Chronicle.id)
        results = search_utils.paginate(
            query=query,
            per_page=2,
            page=1,
        )
        assert results.page == 1
        assert results.total == 7
        assert results.per_page == 2
        assert results.pages == 4
        assert [i.id for i in results.items] == [chronicles[0].id, chronicles[1].id]

    def test_paginate_last_page(self):
        chronicles = chronicles_factories.ChronicleFactory.create_batch(7)
        query = db.session.query(chronicles_models.Chronicle.id).order_by(chronicles_models.Chronicle.id)
        results = search_utils.paginate(
            query=query,
            per_page=2,
            page=4,
        )
        assert results.page == 4
        assert results.total == 7
        assert results.per_page == 2
        assert results.pages == 4
        assert [i.id for i in results.items] == [chronicles[6].id]

    def test_paginate_exact_pages(self):
        chronicles_factories.ChronicleFactory.create_batch(6)
        query = db.session.query(chronicles_models.Chronicle.id).order_by(chronicles_models.Chronicle.id)
        results = search_utils.paginate(
            query=query,
            per_page=2,
            page=1,
        )
        assert results.page == 1
        assert results.total == 6
        assert results.per_page == 2
        assert results.pages == 3

    def test_page_zero(self):
        chronicles_factories.ChronicleFactory.create_batch(1)
        query = db.session.query(chronicles_models.Chronicle.id).order_by(chronicles_models.Chronicle.id)
        with pytest.raises(NotFound):
            search_utils.paginate(
                query=query,
                per_page=2,
                page=0,
            )

    def test_after_last_page(self):
        chronicles_factories.ChronicleFactory.create_batch(1)
        query = db.session.query(chronicles_models.Chronicle.id).order_by(chronicles_models.Chronicle.id)
        with pytest.raises(NotFound):
            search_utils.paginate(
                query=query,
                per_page=2,
                page=2,
            )

    def test_no_results(self):
        query = db.session.query(chronicles_models.Chronicle.id).order_by(chronicles_models.Chronicle.id)
        results = search_utils.paginate(
            query=query,
            per_page=2,
            page=1,
        )
        assert results.page == 1
        assert results.total == 0
        assert results.per_page == 2
        assert results.pages == 0
