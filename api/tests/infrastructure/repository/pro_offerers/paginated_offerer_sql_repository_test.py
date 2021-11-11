import pytest

from pcapi.core.users import factories as users_factories
from pcapi.domain.pro_offerers.paginated_offerers import PaginatedOfferers
from pcapi.infrastructure.repository.pro_offerers.paginated_offerers_sql_repository import (
    PaginatedOfferersSQLRepository,
)
from pcapi.model_creators.generic_creators import create_offerer
from pcapi.model_creators.generic_creators import create_user_offerer
from pcapi.model_creators.generic_creators import create_venue
from pcapi.repository import repository


class PaginatedOffererSQLRepositoryTest:
    @pytest.mark.usefixtures("db_session")
    def should_only_return_offerers_linked_to_user(self, app):
        # Given
        pro = users_factories.ProFactory()
        offerer1 = create_offerer()
        offerer2 = create_offerer(siren="912345678")
        user_offerer = create_user_offerer(user=pro, offerer=offerer1)
        repository.save(user_offerer, offerer2)

        # When
        paginated_offerers = PaginatedOfferersSQLRepository().with_status_and_keywords(
            user_id=pro.id,
            user_is_admin=pro.isAdmin,
            is_filtered_by_offerer_status=False,
            only_validated_offerers=None,
            pagination_limit=10,
            keywords=None,
            page=0,
        )

        # Then
        assert isinstance(paginated_offerers, PaginatedOfferers)
        assert paginated_offerers.total == 1
        assert len(paginated_offerers.offerers) == 1
        assert paginated_offerers.offerers[0].userHasAccess == True

    @pytest.mark.usefixtures("db_session")
    def should_return_linked_offerers_with_matching_keywords_in_name(self, app):
        # Given
        pro = users_factories.ProFactory()
        offerer1 = create_offerer(name="Theatre")
        offerer2 = create_offerer(name="Cinema", siren="912345678")
        venue1 = create_venue(offerer=offerer1, siret=None, is_virtual=True)
        venue2 = create_venue(offerer=offerer2, siret=None, is_virtual=True)
        user_offerer1 = create_user_offerer(user=pro, offerer=offerer1)
        user_offerer2 = create_user_offerer(user=pro, offerer=offerer2)
        repository.save(user_offerer1, user_offerer2, venue1, venue2)

        # When
        paginated_offerers = PaginatedOfferersSQLRepository().with_status_and_keywords(
            user_id=pro.id,
            user_is_admin=pro.isAdmin,
            is_filtered_by_offerer_status=False,
            only_validated_offerers=None,
            pagination_limit=10,
            keywords="Cinema",
            page=0,
        )

        # Then
        assert isinstance(paginated_offerers, PaginatedOfferers)
        assert paginated_offerers.total == 1
        assert len(paginated_offerers.offerers) == 1

    @pytest.mark.usefixtures("db_session")
    def should_return_linked_offerers_with_matching_keywords_in_venue_name(self, app):
        # Given
        pro = users_factories.ProFactory()
        offerer1 = create_offerer(name="Theatre")
        offerer2 = create_offerer(name="Cinema", siren="912345678")
        venue1 = create_venue(name="Les fleurs", offerer=offerer1, siret=None, is_virtual=True)
        venue2 = create_venue(name="Les jardins du vide", offerer=offerer2, siret=None, is_virtual=True)
        user_offerer1 = create_user_offerer(user=pro, offerer=offerer1)
        user_offerer2 = create_user_offerer(user=pro, offerer=offerer2)
        repository.save(user_offerer1, user_offerer2, venue1, venue2)

        # When
        paginated_offerers = PaginatedOfferersSQLRepository().with_status_and_keywords(
            user_id=pro.id,
            user_is_admin=pro.isAdmin,
            is_filtered_by_offerer_status=False,
            only_validated_offerers=None,
            pagination_limit=10,
            keywords="jardins",
            page=0,
        )

        # Then
        assert isinstance(paginated_offerers, PaginatedOfferers)
        assert paginated_offerers.total == 1
        assert len(paginated_offerers.offerers) == 1

    @pytest.mark.usefixtures("db_session")
    def should_return_only_one_offerers_when_it_has_multiple_venues(self, app):
        # Given
        pro = users_factories.ProFactory()
        offerer1 = create_offerer(name="Theatre")
        venue1 = create_venue(name="Les fleurs", offerer=offerer1, siret=None, is_virtual=True)
        venue2 = create_venue(name="Les jardins du vide", offerer=offerer1, siret=None, is_virtual=True)
        user_offerer1 = create_user_offerer(user=pro, offerer=offerer1)
        repository.save(user_offerer1, venue1, venue2)

        # When
        paginated_offerers = PaginatedOfferersSQLRepository().with_status_and_keywords(
            user_id=pro.id,
            user_is_admin=pro.isAdmin,
            is_filtered_by_offerer_status=False,
            only_validated_offerers=None,
            pagination_limit=10,
            keywords=None,
            page=0,
        )

        # Then
        assert isinstance(paginated_offerers, PaginatedOfferers)
        assert paginated_offerers.total == 1
        assert len(paginated_offerers.offerers) == 1

    @pytest.mark.usefixtures("db_session")
    def should_filter_out_non_validated_offerers(self, app):
        # Given
        pro = users_factories.ProFactory()
        offerer1 = create_offerer(validation_token="RTYUIO")
        offerer2 = create_offerer(siren="987654310")
        user_offerer1 = create_user_offerer(user=pro, offerer=offerer1)
        user_offerer2 = create_user_offerer(user=pro, offerer=offerer2)
        repository.save(user_offerer1, user_offerer2)

        # When
        paginated_offerers = PaginatedOfferersSQLRepository().with_status_and_keywords(
            user_id=pro.id,
            user_is_admin=pro.isAdmin,
            is_filtered_by_offerer_status=True,
            only_validated_offerers=True,
            pagination_limit=10,
            keywords=None,
            page=0,
        )

        # Then
        assert isinstance(paginated_offerers, PaginatedOfferers)
        assert paginated_offerers.total == 1
        assert len(paginated_offerers.offerers) == 1
        assert paginated_offerers.offerers[0].id == offerer2.id
