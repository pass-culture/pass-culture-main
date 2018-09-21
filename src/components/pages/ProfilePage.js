/* eslint
  react/jsx-one-expression-per-line: 0 */
import React from 'react'
import { compose } from 'redux'
import PropTypes from 'prop-types'
import { connect } from 'react-redux'
import { withLogin } from 'pass-culture-shared'
import { Route, Switch, withRouter } from 'react-router-dom'

import { getDepartementByCode } from '../../helpers'
import NotMatch from './NotMatch'
import Loader from '../layout/Loader'
import ProfileMainView from './profile/ProfileMainView'
import ProfileEditForm from './profile/forms/ProfileEditForm'
import ProfileUpdateSuccess from './profile/ProfileUpdateSuccess'
import ProfilePasswordForm from './profile/forms/ProfilePasswordForm'

const informationFields = [
  // FIXME -> ajouter une proptypes custom pour pouvoir vérifier dans les vues
  // que l'objet recu pour les définitions des fields du formulaires est valide
  {
    disabled: false,
    key: 'publicName',
    label: 'Identifiant',
    resolver: null,
    type: 'text',
  },
  {
    disabled: true,
    key: ['firstname', 'lastname'],
    label: 'Nom et prénom',
    placeholder: 'Renseigner mon nom et prénom',
    resolver: (user, [firstnameKey, lastnameKey]) => {
      let result = user[firstnameKey] || ''
      result = (result && ' ') || ''
      return `${result}${user[lastnameKey] || ''}`
    },
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
    placeholder: 'Changer mon mot de passe',
    resolver: () => false,
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
          key="route-profile-update-success"
          render={() => <ProfileUpdateSuccess fields={informationFields} />}
        />
        <Route
          exact
          path="/profil/password"
          key="route-profile-password-form"
          render={() => <ProfilePasswordForm fields={informationFields} />}
        />
        <Route
          exact
          path="/profil/:view(password|profil)"
          key="route-profile-edit-form"
          render={() => <ProfileEditForm fields={informationFields} />}
        />
        <Route
          component={route => <NotMatch {...route} redirect="/profil" />}
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
