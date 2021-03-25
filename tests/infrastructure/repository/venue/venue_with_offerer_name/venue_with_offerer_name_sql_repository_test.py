import pytest

import pcapi.core.offers.factories as offers_factories
import pcapi.core.users.factories as users_factories
from pcapi.domain.identifier.identifier import Identifier
from pcapi.domain.venue.venue_with_offerer_name.venue_with_offerer_name import VenueWithOffererName
from pcapi.infrastructure.repository.venue.venue_with_offerer_name import venue_with_offerer_name_domain_converter
from pcapi.infrastructure.repository.venue.venue_with_offerer_name.venue_with_offerer_name_sql_repository import (
    VenueWithOffererNameSQLRepository,
)
from pcapi.model_creators.generic_creators import create_offerer
from pcapi.model_creators.generic_creators import create_user
from pcapi.model_creators.generic_creators import create_user_offerer
from pcapi.model_creators.generic_creators import create_venue
from pcapi.repository import repository


class GetByProIdentifierTest:
    def setup_method(self):
        self.venue_sql_repository = VenueWithOffererNameSQLRepository()

    @pytest.mark.usefixtures("db_session")
    def should_return_only_venues_of_pro_user(self, app: object):
        # given
        pro_user = create_user()
        offerer = create_offerer()
        other_offerer = create_offerer(siren="987654321")
        create_user_offerer(user=pro_user, offerer=offerer)
        venue_1 = create_venue(offerer=offerer, siret="12345678912345")
        venue_2 = create_venue(offerer=offerer, siret="12345678998765")
        venue_not_affiliated_to_pro_user = create_venue(offerer=other_offerer, siret="98765432198765")

        repository.save(venue_1, venue_2, venue_not_affiliated_to_pro_user)

        expected_venue_1 = venue_with_offerer_name_domain_converter.to_domain(venue_1)
        expected_venue_2 = venue_with_offerer_name_domain_converter.to_domain(venue_2)

        # when
        found_venues = self.venue_sql_repository.get_by_pro_identifier(pro_user.id, False, False)

        # then
        assert len(found_venues) == 2
        assert isinstance(found_venues[0], VenueWithOffererName)
        found_venues_id = [venue.identifier for venue in found_venues]
        assert set(found_venues_id) == {expected_venue_1.identifier, expected_venue_2.identifier}

    @pytest.mark.usefixtures("db_session")
    def should_return_all_existing_venues_for_admin_user(self, app: object):
        # given
        admin_user = users_factories.UserFactory(isBeneficiary=False, isAdmin=True)
        offerer = offers_factories.OffererFactory()
        offers_factories.UserOffererFactory(offerer=offerer)
        venue_1 = offers_factories.VenueFactory(managingOfferer=offerer)

        other_offerer = offers_factories.OffererFactory()
        offers_factories.UserOffererFactory(offerer=other_offerer)
        venue_2 = offers_factories.VenueFactory(managingOfferer=other_offerer)

        expected_venue_1 = venue_with_offerer_name_domain_converter.to_domain(venue_1)
        expected_venue_2 = venue_with_offerer_name_domain_converter.to_domain(venue_2)

        # when
        found_venues = self.venue_sql_repository.get_by_pro_identifier(
            pro_identifier=admin_user.id, user_is_admin=True, active_offerers_only=False
        )

        # then
        assert len(found_venues) == 2
        assert isinstance(found_venues[0], VenueWithOffererName)
        found_venues_id = [venue.identifier for venue in found_venues]
        assert set(found_venues_id) == {expected_venue_1.identifier, expected_venue_2.identifier}

    @pytest.mark.usefixtures("db_session")
    def should_return_empty_list_when_no_venues_exist(self, app: object):
        # given
        pro_user = create_user()
        offerer = create_offerer()
        user_offerer = create_user_offerer(user=pro_user, offerer=offerer)
        repository.save(user_offerer)

        # when
        found_venues = self.venue_sql_repository.get_by_pro_identifier(pro_user.id, False, False)

        # then
        assert found_venues == []

    @pytest.mark.usefixtures("db_session")
    def should_return_all_venues_of_pro_user_ordered_by_name(self, app: object):
        # given
        pro_user = create_user()
        offerer = create_offerer()
        create_user_offerer(user=pro_user, offerer=offerer)
        venue_1 = create_venue(offerer=offerer, siret="12345678912345", name="B")
        venue_2 = create_venue(offerer=offerer, siret="98765432198765", name="A")

        repository.save(venue_1, venue_2)

        expected_venue_1 = venue_with_offerer_name_domain_converter.to_domain(venue_1)
        expected_venue_2 = venue_with_offerer_name_domain_converter.to_domain(venue_2)

        # when
        found_venues = self.venue_sql_repository.get_by_pro_identifier(pro_user.id, False, False)

        # then
        assert len(found_venues) == 2
        assert found_venues[0].name == expected_venue_2.name
        assert found_venues[1].name == expected_venue_1.name

    @pytest.mark.usefixtures("db_session")
    def should_not_return_venues_of_non_validated_offerer(self, app: object):
        # given
        pro_user = users_factories.UserFactory(isBeneficiary=False)
        offerer = offers_factories.OffererFactory()
        offers_factories.UserOffererFactory(user=pro_user, offerer=offerer)
        venue_of_validated_offerer = offers_factories.VenueFactory(managingOfferer=offerer)

        offerer_not_validated = offers_factories.OffererFactory(validationToken="token")
        offers_factories.UserOffererFactory(user=pro_user, offerer=offerer_not_validated)
        offers_factories.VenueFactory(managingOfferer=offerer_not_validated)

        expected_venue = venue_with_offerer_name_domain_converter.to_domain(venue_of_validated_offerer)

        # when
        found_venues = self.venue_sql_repository.get_by_pro_identifier(
            pro_identifier=pro_user.id,
            user_is_admin=False,
            active_offerers_only=False,
            validated_offerer=True,
        )

        # then
        assert len(found_venues) == 1
        assert found_venues[0].name == expected_venue.name

    @pytest.mark.usefixtures("db_session")
    def should_not_return_venues_of_non_validated_user_offerer(self, app: object):
        # given
        pro_user = users_factories.UserFactory(isBeneficiary=False)
        offerer = offers_factories.OffererFactory()
        offers_factories.UserOffererFactory(user=pro_user, offerer=offerer, validationToken="token")
        offers_factories.VenueFactory(managingOfferer=offerer)

        # when
        found_venues = self.venue_sql_repository.get_by_pro_identifier(
            pro_identifier=pro_user.id,
            user_is_admin=False,
            active_offerers_only=False,
            validated_offerer_for_user=True,
        )

        # then
        assert len(found_venues) == 0

    @pytest.mark.usefixtures("db_session")
    def should_return_venues_filtered_by_offerer_id_when_provided(self, app: object):
        # given
        pro_user = create_user()
        wanted_offerer = create_offerer(idx=1)
        unwanted_offerer = create_offerer(idx=2, siren="5654367")
        create_user_offerer(user=pro_user, offerer=wanted_offerer)
        create_user_offerer(user=pro_user, offerer=unwanted_offerer)
        venue_from_wanted_offerer = create_venue(
            name="Kléber", offerer=wanted_offerer, siret="12345678912345", public_name="Librairie Kléber"
        )
        venue_from_unwanted_offerer = create_venue(name="QG FNAC", offerer=unwanted_offerer, siret="98765432198765")

        repository.save(venue_from_wanted_offerer, venue_from_unwanted_offerer)

        # when
        found_venues = self.venue_sql_repository.get_by_pro_identifier(
            pro_identifier=pro_user.id, user_is_admin=False, active_offerers_only=False, offerer_id=Identifier(1)
        )

        # then
        assert len(found_venues) == 1
        assert found_venues[0].name == venue_from_wanted_offerer.name

    @pytest.mark.usefixtures("db_session")
    def should_not_return_venues_with_inactive_offerer_for_validated_user_offerer(self, app):
        # given
        pro_user = users_factories.UserFactory(isBeneficiary=False)
        active_offerer = offers_factories.OffererFactory(isActive=True)
        inactive_offerer = offers_factories.OffererFactory(isActive=False)
        offers_factories.UserOffererFactory(user=pro_user, offerer=active_offerer)
        offers_factories.UserOffererFactory(user=pro_user, offerer=inactive_offerer)
        venue_from_active_offerer = offers_factories.VenueFactory(
            name="venue_from_active_offerer", managingOfferer=active_offerer
        )
        offers_factories.VenueFactory(name="venue_from_inactive_offerer", managingOfferer=inactive_offerer)

        # when
        found_venues = self.venue_sql_repository.get_by_pro_identifier(
            pro_identifier=pro_user.id,
            user_is_admin=False,
            active_offerers_only=True,
        )

        # then
        assert len(found_venues) == 1
        assert found_venues[0].name == venue_from_active_offerer.name
