from io import BytesIO

from repository.repository import Repository
from tests.conftest import clean_database, TestClient
from tests.files.transactions import VALID_MESSAGE
from tests.model_creators.generic_creators import create_user, create_payment_message


class Post:
    class Returns200:
        @clean_database
        def when_file_authenticity_is_certified(self, app):
            # given
            user = create_user(can_book_free_offers=False, is_admin=True)
            payment_message = create_payment_message(
                name='passCulture-SCT-20181015-114356',
                checksum=b'\x86\x05[(j\xfd\x111l\xd7\xca\xcd\x00\xe6\x104\xfd\xde\xdd\xa5\x0c#L\x01W\xa8\xf0\xdan0\x93\x1e'
            )
            Repository.save(user, payment_message)

            auth_request = TestClient(app.test_client()).with_auth(email=user.email)

            # when
            response = auth_request.post(
                '/validate/payment_message',
                files={'file': (BytesIO(VALID_MESSAGE.encode('utf-8')), 'message.xml')}
            )

            # then
            assert response.status_code == 200
            assert response.json['checksum'] == '86055b286afd11316cd7cacd00e61034fddedda50c234c0157a8f0da6e30931e'

    class Returns400:
        @clean_database
        def when_given_checksum_does_not_match_known_checksum(self, app):
            # given
            user = create_user(can_book_free_offers=False, is_admin=True)
            payment_message = create_payment_message(
                name='passCulture-SCT-20181015-114356',
                checksum=b'FAKE_CHECKSUM'
            )
            Repository.save(user, payment_message)

            auth_request = TestClient(app.test_client()).with_auth(email=user.email)

            # when
            response = auth_request.post(
                '/validate/payment_message',
                files={'file': (BytesIO(VALID_MESSAGE.encode('utf-8')), 'message.xml')}
            )

            # then
            assert response.status_code == 400
            assert response.json['xml'] == [
                "L'intégrité du document n'est pas validée car la somme de contrôle est invalide : "
                "86055b286afd11316cd7cacd00e61034fddedda50c234c0157a8f0da6e30931e"
            ]

    class Returns401:
        @clean_database
        def when_current_user_is_not_logged_in(self, app):
            # when
            response = TestClient(app.test_client()).post(
                '/validate/payment_message',
                files={'file': (BytesIO(VALID_MESSAGE.encode('utf-8')), 'message.xml')},
                headers={'origin': 'http://localhost:3000'}
            )

            # then
            assert response.status_code == 401

    class Returns403:
        @clean_database
        def when_current_user_is_not_admin(self, app):
            # given
            user = create_user(can_book_free_offers=True, is_admin=False)
            message = create_payment_message(
                name='passCulture-SCT-20181015-114356',
                checksum=b'\x86\x05[(j\xfd\x111l\xd7\xca\xcd\x00\xe6\x104\xfd\xde\xdd\xa5\x0c#L\x01W\xa8\xf0\xdan0\x93\x1e'
            )
            Repository.save(user, message)

            auth_request = TestClient(app.test_client()).with_auth(email=user.email)

            # when
            response = auth_request.post(
                '/validate/payment_message',
                files={'file': (BytesIO(VALID_MESSAGE.encode('utf-8')), 'message.xml')}
            )

            # then
            assert response.status_code == 403

    class Returns404:
        @clean_database
        def when_id_from_file_is_unknown(self, app):
            # given
            user = create_user(can_book_free_offers=False, is_admin=True)
            Repository.save(user)

            auth_request = TestClient(app.test_client()).with_auth(email=user.email)

            # when
            response = auth_request.post(
                '/validate/payment_message',
                files={'file': (BytesIO(VALID_MESSAGE.encode('utf-8')), 'message.xml')}
            )

            # then
            assert response.status_code == 404
            assert response.json['xml'] == [
                "L'identifiant du document XML 'MsgId' est inconnu"
            ]
