import pytest

import pcapi.core.offerers.factories as offerers_factories
from pcapi.scripts.business_unit.rename_bu_not_matching_venue_public_name import (
    rename_bu_not_matching_venue_public_name,
)


@pytest.mark.usefixtures("db_session")
class RenameBuNotMatchingVenuePublicNameTest:
    def test_rename_bu_not_matching_venue_public_name(self):
        # Given
        venue1 = offerers_factories.VenueFactory(
            businessUnit__name="Point de remboursement #1",
            businessUnit__siret="11111111100000",
            managingOfferer__siren="111111111",
            siret="11111111100000",
        )
        venue2 = offerers_factories.VenueFactory(
            businessUnit__name="Point de remboursement #2",
            businessUnit__siret=None,
            managingOfferer__siren="222222222",
            siret="22222222200000",
        )
        venue3 = offerers_factories.VenueFactory(
            businessUnit__name="Point de remboursement #3",
            businessUnit__siret="33333333300000",
            managingOfferer__siren="333333333",
            siret="33333333300000",
            publicName=None,
        )

        bu_with_siret = venue1.businessUnit
        bu_without_siret = venue2.businessUnit
        bu_venue_without_public_name = venue3.businessUnit

        # When
        rename_bu_not_matching_venue_public_name()

        # Assert
        assert bu_with_siret.name == venue1.publicName
        assert bu_without_siret.name != venue2.publicName
        assert bu_venue_without_public_name.name == venue3.name
