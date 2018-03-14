from utils.test_utils import API_URL, req, req_with_auth


BASE_DATA = {
             'email': 'toto@toto.com',
             'publicName': 'Toto',
             'password': 'toto12345678'
            }


def assert_signup_error(data, err_field):
    r_signup = req_with_auth().post(API_URL + '/users',
                                  json=data)
    assert r_signup.status_code == 400
    error = r_signup.json()
    assert err_field in error


def test_10_signup_should_not_work_without_email():
    data = BASE_DATA.copy()
    del(data['email'])
    assert_signup_error(data, 'email')


def test_10_signup_should_not_work_with_invalid_email():
    data = BASE_DATA.copy()
    data['email'] = 'toto'
    assert_signup_error(data, 'email')


def test_10_signup_should_not_work_without_publicName():
    data = BASE_DATA.copy()
    del(data['publicName'])
    assert_signup_error(data, 'publicName')


def test_10_signup_should_not_work_with_invalid_publicName():
    data = BASE_DATA.copy()
    data['publicName'] = 't'
    assert_signup_error(data, 'publicName')
    data = BASE_DATA.copy()
    data['publicName'] = 'x'*32
    assert_signup_error(data, 'publicName')


def test_10_signup_should_not_work_without_password():
    data = BASE_DATA.copy()
    del(data['password'])
    assert_signup_error(data, 'password')


def test_10_signup_should_not_work_with_invalid_password():
    data = BASE_DATA.copy()
    data['password'] = 'short'
    assert_signup_error(data, 'password')


def test_11_signup():
    r_signup = req_with_auth().post(API_URL + '/users',
                                  json=BASE_DATA)
    assert r_signup.status_code == 201
    assert 'Set-Cookie' in r_signup.headers


def test_12_signup_should_not_work_again_with_same_email():
    assert_signup_error(BASE_DATA, 'email')


def test_13_get_profile_should_work_only_when_logged_in():
    r = req.get(API_URL + '/users/me')
    assert r.status_code == 401


def test_14_get_profile_should_return_the_users_profile_without_password_hash():
    r = req_with_auth().get(API_URL + '/users/me')
    assert r.status_code == 200
    user = r.json()
    assert user['email'] == 'erwan.ledoux@beta.gouv.fr'
    assert user['publicName'] == 'Erwan Ledoux'
    assert 'password' not in user
