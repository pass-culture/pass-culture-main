import requests_mock

from pcapi.notifications.push.backends.batch import BatchBackend


class BatchPushNotificationClientTest:
    def test_update_user_attributes(self):
        with requests_mock.Mocker() as mock:
            android_post = mock.post("https://api.example.com/fake_android_api_key/data/users/1")
            ios_post = mock.post("https://api.example.com/fake_ios_api_key/data/users/1")

            BatchBackend().update_user_attributes(1, {"attri": "but"})

            assert ios_post.last_request.json() == {"overwrite": False, "values": {"attri": "but"}}
            assert android_post.last_request.json() == {"overwrite": False, "values": {"attri": "but"}}
