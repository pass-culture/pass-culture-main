from utils.test_utils import API_URL, req, req_with_auth


BASE_DATA = {
             'email': 'toto@btmx.fr',
             'publicName': 'Toto',
             'password': 'toto12345678',
             'contact_ok': 'true'
            }


def assert_signup_error(data, err_field):
    r_signup = req.post(API_URL + '/users',
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


def test_10_signup_should_not_work_without_contact_ok():
    data = BASE_DATA.copy()
    del(data['contact_ok'])
    assert_signup_error(data, 'contact_ok')


def test_10_signup_should_not_work_with_invalid_contact_ok():
    data = BASE_DATA.copy()
    data['contact_ok'] = 't'
    assert_signup_error(data, 'contact_ok')


def test_11_signup():
    r_signup = req.post(API_URL + '/users',
                                  json=BASE_DATA)
    assert r_signup.status_code == 201
    assert 'Set-Cookie' in r_signup.headers


def test_12_signup_should_not_work_again_with_same_email():
    assert_signup_error(BASE_DATA, 'email')


def test_13_get_profile_should_work_only_when_logged_in():
    r = req.get(API_URL + '/users/me')
    assert r.status_code == 401


#def test_14_get_profile_should_not_work_if_account_is_not_validated():
#    r = req_with_auth(email='toto@btmx.fr',
#                      password='toto12345678')\
#                    .get(API_URL + '/users/me')
#    assert r.status_code == 401
#    assert 'pas validé' in r.json()['identifier']


#def test_15_should_not_be_able_to_validate_user_with_wrong_token():
#    r = req_with_auth(email='toto@btmx.fr',
#                      password='toto12345678')\
#                 .get(API_URL + '/validate?modelNames=User&token=123')
#    assert r.status_code == 404
 
 
#def test_16_should_be_able_to_validate_user(app):
#    token = app.model.User.query\
#                          .filter(app.model.User.validationToken != None)\
#                          .first().validationToken
#    r = req_with_auth().get(API_URL + '/validate?modelNames=User&token='+token)
#    assert r.status_code == 202


def test_17_get_profile_should_return_the_users_profile_without_password_hash():
    r = req_with_auth(email='toto@btmx.fr',
                      password='toto12345678')\
                 .get(API_URL + '/users/me')
    user = r.json()
    print(user)
    assert r.status_code == 200
    assert user['email'] == 'toto@btmx.fr'
    assert 'password' not in user


def test_18_signup_should_not_work_for_user_not_in_exp_spreadsheet():
    data = BASE_DATA.copy()
    data['email'] = 'unknown@unknown.com'
    assert_signup_error(data, 'email')
