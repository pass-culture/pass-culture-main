/* eslint
  react/jsx-one-expression-per-line: 0 */
import React from 'react'
import { compose } from 'redux'
import PropTypes from 'prop-types'
import { connect } from 'react-redux'
import { withLogin } from 'pass-culture-shared'
import { Route, Switch, withRouter } from 'react-router-dom'

import { getDepartementByCode } from '../../helpers'
import Loader from '../layout/Loader'
import ProfileEditView from '../profile/ProfileEditView'
import ProfileMainView from '../profile/ProfileMainView'
import ProfilePasswordView from '../profile/ProfilePasswordView'
import ProfileUpdateSuccess from '../profile/ProfileUpdateSuccess'

const informationFields = [
  {
    disabled: false,
    key: 'publicName',
    label: 'Identifiant',
    resolver: null,
    type: 'text',
  },
  {
    disabled: true,
    key: 'firstnameLastname',
    label: 'Nom et prénom',
    resolver: null,
    type: 'text',
  },
  {
    disabled: true,
    key: 'email',
    label: 'Adresse e-mail',
    resolver: null,
    type: 'email',
  },
  {
    disabled: false,
    key: 'password',
    label: 'Mot de passe',
    resolver: () => '**********',
    type: 'password',
  },
  {
    disabled: true,
    key: 'departementCode',
    label: 'Département de résidence',
    resolver: (user, key) => {
      const code = user[key]
      const deptname = getDepartementByCode(code)
      return `${code} - ${deptname}`
    },
    type: 'select',
  },
]

const ProfilePage = ({ isloaded, location }) => (
  <div id="profile-page" className="page is-relative">
    {isloaded && (
      <Switch location={location}>
        <Route
          exact
          path="/profil"
          key="route-profile-main-view"
          render={() => <ProfileMainView fields={informationFields} />}
        />
        <Route
          exact
          path="/profil/:view?/success"
          key="route-profile-password-view"
          render={() => <ProfileUpdateSuccess fields={informationFields} />}
        />
        <Route
          exact
          path="/profil/password"
          key="route-profile-password-view"
          render={() => <ProfilePasswordView fields={informationFields} />}
        />
        <Route
          exact
          path="/profil/:view"
          key="route-profile-edit-view"
          render={() => <ProfileEditView fields={informationFields} />}
        />
      </Switch>
    )}
    {!isloaded && <Loader isloading />}
  </div>
)

ProfilePage.propTypes = {
  isloaded: PropTypes.bool.isRequired,
  location: PropTypes.object.isRequired,
}

const mapStateToProps = state => {
  const user = state.user || false
  const isloaded = (user && user !== null) || typeof user === 'object'
  return { isloaded }
}

export default compose(
  withRouter,
  withLogin({ failRedirect: '/connexion' }),
  connect(mapStateToProps)
)(ProfilePage)
