import PropTypes from 'prop-types'
import React, { PureComponent } from 'react'
import { Route, Switch } from 'react-router-dom'

import LoaderContainer from '../../layout/Loader/LoaderContainer'
import NotMatch from '../not-match/NotMatch'
import UserPasswordField from './forms/fields/UserPasswordField'
import ProfileMainView from './ProfileMainView/ProfileMainView'
import ProfileUpdateSuccess from './ProfileUpdateSuccess/ProfileUpdateSuccess'

class Profile extends PureComponent {
  renderProfileMainView = currentUser => () => <ProfileMainView currentUser={currentUser} />

  renderPasswordUpdateSuccess = routeProps => (
    <ProfileUpdateSuccess
      {...routeProps}
      title="Votre mot de passe"
    />
  )

  renderPasswordEditForm = routeProps => (
    <UserPasswordField
      {...routeProps}
      title="Votre mot de passe"
    />
  )

  renderNoMatch = routeProps => (<NotMatch
    {...routeProps}
    delay={3}
    redirect="/profil"
                                 />)

  render() {
    const { currentUser, location } = this.props

    return (
      <div
        className="page is-relative"
        id="profile-page"
      >
        {currentUser && (
          <Switch location={location}>
            <Route
              exact
              key="route-profile-main-view"
              path="/profil/:menu(menu)?"
              render={this.renderProfileMainView(currentUser)}
            />
            <Route
              exact
              key="route-profile-update-success"
              path="/profil/:view(password)/success/:menu(menu)?"
              render={this.renderPasswordUpdateSuccess}
            />
            <Route
              exact
              key="route-profile-edit-form"
              path="/profil/:view(password)/:menu(menu)?"
              render={this.renderPasswordEditForm}
            />
            <Route component={this.renderNoMatch} />
          </Switch>
        )}
        {!currentUser && <LoaderContainer isLoading />}
      </div>
    )
  }
}

Profile.propTypes = {
  currentUser: PropTypes.shape().isRequired,
  location: PropTypes.shape().isRequired,
}

export default Profile
