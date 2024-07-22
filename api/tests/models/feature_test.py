import enum
from unittest.mock import patch

import flask
import pytest

from pcapi.core.testing import assert_num_queries
from pcapi.models import db
from pcapi.models.feature import FEATURES_DISABLED_BY_DEFAULT
from pcapi.models.feature import Feature
from pcapi.models.feature import FeatureToggle
from pcapi.models.feature import check_feature_flags_completeness
from pcapi.models.feature import clean_feature_flags
from pcapi.models.feature import install_feature_flags
from pcapi.repository import repository


class TestingFeatureToggle(enum.Enum):
    AUTO_DESTROY_AIRCRAFT_ON_WINDOW_OPENING = "Auto destruction programmée lors d'une ouverture de la fenêtre"
    ENABLE_LANDING = "Autoriser l'atterrissage"
    ENABLE_LOOPING_INOPINE = "Autorise le départ en looping inopiné"


FEATURES_DISABLED_BY_DEFAULT_TEST = [TestingFeatureToggle.ENABLE_LANDING]


@pytest.mark.usefixtures("db_session")
class FeatureToggleTest:
    def test_is_active_returns_true_when_feature_is_active(self):
        # Given
        feature = Feature.query.filter_by(name=FeatureToggle.SYNCHRONIZE_ALLOCINE.name).first()
        feature.isActive = True
        repository.save(feature)

        # When / Then
        assert FeatureToggle.SYNCHRONIZE_ALLOCINE.is_active()

    def test_is_active_returns_false_when_feature_is_inactive(self):
        # Given
        feature = Feature.query.filter_by(name=FeatureToggle.SYNCHRONIZE_ALLOCINE.name).first()
        feature.isActive = False
        repository.save(feature)
        # When / Then
        assert not FeatureToggle.SYNCHRONIZE_ALLOCINE.is_active()

    def test_is_active_query_count_inside_request_context(self):
        feature = Feature.query.filter_by(name=FeatureToggle.SYNCHRONIZE_ALLOCINE.name).first()
        feature.isActive = True
        repository.save(feature)

        with assert_num_queries(1):
            FeatureToggle.SYNCHRONIZE_ALLOCINE.is_active()
            FeatureToggle.SYNCHRONIZE_ALLOCINE.is_active()
            FeatureToggle.SYNCHRONIZE_ALLOCINE.is_active()

    def test_is_active_query_count_outside_request_context(self, app):
        feature = Feature.query.filter_by(name=FeatureToggle.SYNCHRONIZE_ALLOCINE.name).first()
        feature.isActive = True
        repository.save(feature)
        context = flask._request_ctx_stack.pop()

        # we don't cache yet outside the scope of a request so it'll be 3 DB queries
        try:
            with assert_num_queries(3):
                FeatureToggle.SYNCHRONIZE_ALLOCINE.is_active()
                FeatureToggle.SYNCHRONIZE_ALLOCINE.is_active()
                FeatureToggle.SYNCHRONIZE_ALLOCINE.is_active()

        finally:
            flask._request_ctx_stack.push(context)

    def test_one_request_for_all_flags(self):
        with assert_num_queries(1):
            FeatureToggle.SYNCHRONIZE_ALLOCINE.is_active()
            FeatureToggle.DISABLE_CGR_EXTERNAL_BOOKINGS.is_active()
            FeatureToggle.ALGOLIA_BOOKINGS_NUMBER_COMPUTATION.is_active()


@pytest.mark.usefixtures("db_session")
class FeatureTest:
    def test_features_installation(self):
        # assert all defined feature flags are present in the database with the right initial value
        for flag in list(FeatureToggle):
            assert Feature.query.filter_by(name=flag.name).first().isActive == (
                flag not in FEATURES_DISABLED_BY_DEFAULT
            )


@pytest.mark.usefixtures("db_session")
@patch("pcapi.models.feature.FeatureToggle", TestingFeatureToggle)
@patch("pcapi.models.feature.FEATURES_DISABLED_BY_DEFAULT", FEATURES_DISABLED_BY_DEFAULT_TEST)
def test_install_feature_flags(app, caplog):
    Feature.query.delete()

    declared_and_installed = Feature(
        name=TestingFeatureToggle.AUTO_DESTROY_AIRCRAFT_ON_WINDOW_OPENING.name,
        description=TestingFeatureToggle.AUTO_DESTROY_AIRCRAFT_ON_WINDOW_OPENING.value,
        isActive=False,
    )
    db.session.add(declared_and_installed)
    db.session.flush()
    install_feature_flags()

    # already installed keeps isActive value
    assert not Feature.query.filter_by(name=declared_and_installed.name).one().isActive

    # new installed with isActive=True
    assert Feature.query.filter_by(name=TestingFeatureToggle.ENABLE_LOOPING_INOPINE.name).one().isActive

    # new installed with isActive=False


@pytest.mark.usefixtures("db_session")
@patch("pcapi.models.feature.FeatureToggle", TestingFeatureToggle)
def test_feature_flag_completeness(app, caplog):
    Feature.query.delete()
    declared_and_installed = Feature(
        name=TestingFeatureToggle.AUTO_DESTROY_AIRCRAFT_ON_WINDOW_OPENING.name,
        description=TestingFeatureToggle.AUTO_DESTROY_AIRCRAFT_ON_WINDOW_OPENING.value,
        isActive=False,
    )

    not_declared_but_installed = Feature(
        name="ENABLE_TAKEOFF", isActive=False, description="Veillez à bien laisser ce feature flag désactivé"
    )

    db.session.add(declared_and_installed)
    db.session.add(not_declared_but_installed)
    db.session.flush()

    install_feature_flags()
    check_feature_flags_completeness()
    assert caplog.messages == [
        "The following feature flags are present in the database but not present in the code: {'ENABLE_TAKEOFF'}"
    ]


@pytest.mark.usefixtures("db_session")
@patch("pcapi.models.feature.FeatureToggle", TestingFeatureToggle)
def test_clean_feature_flags(app):
    Feature.query.delete()
    install_feature_flags()
    old_feature = Feature(
        name="old_feature",
        description="old_feature_desctiption",
    )
    db.session.add(old_feature)
    db.session.flush()

    clean_feature_flags()

    assert Feature.query.filter_by(name="old_feature").one_or_none() is None
    assert Feature.query.count() == len(TestingFeatureToggle)
