import pytest

from pcapi.utils import crypto


class DevEnvironmentPasswordHasherTest:
    @pytest.mark.settings(USE_FAST_AND_INSECURE_PASSWORD_HASHING_ALGORITHM=True)
    def test_hash_password_uses_md5(self):
        hashed = crypto.hash_password("secret")
        assert hashed == b"5ebe2294ecd0e0f08eab7690d2a6ee69"

    def test_check_password(self):
        hashed = crypto.hash_password("secret")
        assert not crypto.check_password("wrong", hashed)
        assert crypto.check_password("secret", hashed)

    def test_check_public_api_key(self):
        hashed = crypto.hash_public_api_key("secret")
        assert not crypto.check_public_api_key("wrong", hashed)
        assert crypto.check_public_api_key("secret", hashed)

    def test_no_password_leak(self):
        non_unicode_password = "user@AZERTY123\udee0"

        with pytest.raises(Exception) as exception:
            crypto.hash_password(non_unicode_password)

        assert "user@AZERTY123" not in str(exception), str(exception)


class ProdEnvironmentPasswordHasherTest:
    @pytest.mark.settings(USE_FAST_AND_INSECURE_PASSWORD_HASHING_ALGORITHM=False)
    def test_hash_password_uses_bcrypt(self):
        hashed = crypto.hash_password("secret")
        assert hashed != "secret"
        assert hashed.startswith(b"$2b$")  # bcrypt prefix

    @pytest.mark.settings(USE_FAST_AND_INSECURE_PASSWORD_HASHING_ALGORITHM=False)
    def test_hash_public_api_key_uses_sha3_512(self):
        hashed = crypto.hash_public_api_key("secret")
        assert hashed != "secret"
        assert hashed.startswith(b"$sha3_512$")

    def test_check_password(self):
        hashed = crypto.hash_password("secret")
        assert not crypto.check_password("wrong", hashed)
        assert crypto.check_password("secret", hashed)

    def test_check_public_api_key(self):
        hashed = crypto.hash_public_api_key("secret")
        assert not crypto.check_public_api_key("wrong", hashed)
        assert crypto.check_public_api_key("secret", hashed)

    def test_no_password_leak(self):
        non_unicode_password = "user@AZERTY123\udee0"

        with pytest.raises(Exception) as exception:
            crypto.hash_password(non_unicode_password)

        assert "user@AZERTY123" not in str(exception), str(exception)


class EncryptDataTest:
    def test_we_can_cipher_sensitive_data(self):
        sensitive_data = "ultra_sensitive_data"
        encrypted_text = crypto.encrypt(sensitive_data)
        assert sensitive_data != encrypted_text
        decrypted_text = crypto.decrypt(encrypted_text)
        assert sensitive_data == decrypted_text
