import pytest
from wtforms import Form
from wtforms import ValidationError

from pcapi.admin.custom_views.allocine_pivot_view import AllocinePivotView
import pcapi.core.offers.factories as offers_factories
from pcapi.models import AllocinePivot


class AllocinePivotViewTest:
    def test_should_not_allow_creation_for_siret_that_does_not_exit(self, app, db_session):
        # given
        pivot = AllocinePivot(siret="36252187900034")
        view = AllocinePivotView(model=AllocinePivot, session=db_session)

        # when
        with pytest.raises(ValidationError) as error:
            view.on_model_change(Form(), model=pivot)

        # then
        assert str(error.value) == "Le SIRET (36252187900034) n'est associé à aucun lieu"

    def test_should_allow_creation_for_venue_with_siret(self, app, db_session):
        # given
        venue = offers_factories.VenueFactory()
        pivot = AllocinePivot(siret=venue.siret)
        view = AllocinePivotView(model=AllocinePivot, session=db_session)

        # then
        view.on_model_change(Form(), model=pivot)
