from utils.test_utils import API_URL, req_with_auth


def test_10_recommend_offers():
    user = req_with_auth().post(API_URL + '/me')
