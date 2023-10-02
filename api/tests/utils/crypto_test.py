from pcapi.core.testing import override_settings
from pcapi.utils import crypto


class DevEnvironmentPasswordHasherTest:
    def test_hash_password_uses_md5(self):
        hashed = crypto.hash_password("secret")
        assert hashed == b"5ebe2294ecd0e0f08eab7690d2a6ee69"

    def test_check_password(self):
        hashed = crypto.hash_password("secret")
        assert not crypto.check_password("wrong", hashed)
        assert crypto.check_password("secret", hashed)


@override_settings(USE_FAST_AND_INSECURE_PASSWORD_HASHING_ALGORITHM=False)
class ProdEnvironmentPasswordHasherTest:
    def test_hash_password_uses_bcrypt(self):
        hashed = crypto.hash_password("secret")
        assert hashed != "secret"
        assert hashed.startswith(b"$2b$")  # bcrypt prefix

    def test_check_password(self):
        hashed = crypto.hash_password("secret")
        assert not crypto.check_password("wrong", hashed)
        assert crypto.check_password("secret", hashed)


class EncryptDataTest:
    def test_we_can_cipher_sensitive_data(self):
        sensitive_data = "ultra_sensitive_data"
        encrypted_text = crypto.encrypt(sensitive_data)
        assert sensitive_data != encrypted_text
        decrypted_text = crypto.decrypt(encrypted_text)
        assert sensitive_data == decrypted_text
