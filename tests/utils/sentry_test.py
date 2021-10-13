from pcapi.core.testing import override_settings
from pcapi.utils import sentry


@override_settings(IS_DEV=False)
def test_init_sentry_sdk():
    # There is not much to test here, except that the call does not
    # fail.
    sentry.init_sentry_sdk()
