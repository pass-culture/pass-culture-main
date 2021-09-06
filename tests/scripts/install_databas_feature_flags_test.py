import enum
from unittest.mock import patch

import pytest

from pcapi.models import db
from pcapi.models.feature import Feature
from pcapi.scripts.install_database_feature_flags import install_database_feature_flags


class FeatureToggleTest(enum.Enum):
    AUTO_DESTROY_AIRCRAFT_ON_WINDOW_OPENING = "Auto destruction programmée lors d'une ouverture de la fenêtre"
    ENABLE_LANDING = "Autoriser l'atterrissage"
    ENABLE_LOOPING_INOPINE = "Autorise le départ en looping inopiné"


FEATURES_DISABLED_BY_DEFAULT_TEST = [FeatureToggleTest.ENABLE_LANDING]


@pytest.mark.usefixtures("db_session")
@patch("pcapi.models.feature.FeatureToggle", FeatureToggleTest)
@patch("pcapi.models.feature.FEATURES_DISABLED_BY_DEFAULT", FEATURES_DISABLED_BY_DEFAULT_TEST)
def test_install_database_feature_flags(app, caplog):
    Feature.query.delete()

    declared_and_installed = Feature(
        name=FeatureToggleTest.AUTO_DESTROY_AIRCRAFT_ON_WINDOW_OPENING.name,
        description=FeatureToggleTest.AUTO_DESTROY_AIRCRAFT_ON_WINDOW_OPENING.value,
        isActive=False,
    )
    not_declared_but_installed = Feature(
        name="ENABLE_TAKEOFF", isActive=False, description="Veillez à bien laisser ce feature flag désactivé"
    )

    db.session.add(declared_and_installed)
    db.session.add(not_declared_but_installed)
    db.session.commit()

    install_database_feature_flags(app)

    # already installed keeps isActive value
    assert not Feature.query.filter_by(name=declared_and_installed.name).one().isActive

    # new installed with isActive=True
    assert Feature.query.filter_by(name=FeatureToggleTest.ENABLE_LOOPING_INOPINE.name).one().isActive

    # new installed with isActive=False
    assert not Feature.query.filter_by(name=FeatureToggleTest.ENABLE_LANDING.name).one().isActive

    assert caplog.messages == [
        "The following feature flags are present in database but not present in code: {'ENABLE_TAKEOFF'}"
    ]
