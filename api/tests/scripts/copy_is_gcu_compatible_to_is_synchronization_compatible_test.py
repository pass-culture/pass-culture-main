import pytest

from pcapi.core.offers.factories import ProductFactory
from pcapi.scripts.copy_is_gcu_compatible_to_is_syhnchronization_compatible import (
    copy_is_gcu_compatible_to_is_synchronization_compatible,
)


@pytest.mark.usefixtures("db_session")
def test_should_copy_is_gcu_compatible_to_is_synchronization_compatible():
    product_1 = ProductFactory(isGcuCompatible=True, isSynchronizationCompatible=True)
    product_2 = ProductFactory(isGcuCompatible=False, isSynchronizationCompatible=True)
    product_3 = ProductFactory(isGcuCompatible=False, isSynchronizationCompatible=True)
    product_4 = ProductFactory(isGcuCompatible=True, isSynchronizationCompatible=True)
    product_5 = ProductFactory(isGcuCompatible=True, isSynchronizationCompatible=True)
    product_6 = ProductFactory(isGcuCompatible=False, isSynchronizationCompatible=True)

    copy_is_gcu_compatible_to_is_synchronization_compatible(4)

    assert product_1.isSynchronizationCompatible
    assert not product_2.isSynchronizationCompatible
    assert not product_3.isSynchronizationCompatible
    assert product_4.isSynchronizationCompatible
    assert product_5.isSynchronizationCompatible
    assert not product_6.isSynchronizationCompatible
