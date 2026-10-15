import pytest


pytestmark = pytest.mark.usefixtures("db_session")
