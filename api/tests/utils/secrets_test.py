from unittest.mock import patch

import pcapi.utils.secrets as secrets_utils


class SecretsTest:
    @patch("pcapi.utils.secrets.SECRET_KEYS", [])
    def test_print_secrets_in_yaml_format(self):
        secrets_utils.get("FIRST_SECRET")
        secrets_utils.get("FIRST_SECRET")  # Should not appear twice
        secrets_utils.get("SECOND_SECRET", "default_value")
        secrets_utils.get("PRE_SECOND_SECRET")  # Should appear before SECOND_SECRET (alphabetical)

        dumpped_secret_keys = secrets_utils.dump_secret_keys()
        assert (
            dumpped_secret_keys
            == """secrets:
- name: FIRST_SECRET
- name: PRE_SECOND_SECRET
- name: SECOND_SECRET
"""
        )
