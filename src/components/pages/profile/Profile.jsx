import PropTypes from 'prop-types'
import React, { PureComponent } from 'react'
import { Route, Switch } from 'react-router-dom'

import getDepartementByCode from '../../../utils/getDepartementByCode'
import { snackbar } from '../../../utils/snackbar'
import LoaderContainer from '../../layout/Loader/LoaderContainer'
import NotMatch from '../not-match/NotMatch'
import EditPasswordContainer from './EditPassword/EditPasswordContainer'
import PersonalInformationsContainer from './PersonalInformations/PersonalInformationsContainer'
import ProfileMainView from './ProfileMainView/ProfileMainView'
import ProfileUpdateSuccess from './ProfileUpdateSuccess/ProfileUpdateSuccess'

export const getDepartment = departmentCode => {
  const departmentName = getDepartementByCode(departmentCode)
  return `${departmentName} (${departmentCode})`
}

class Profile extends PureComponent {
  renderProfileMainView = currentUser => () => <ProfileMainView currentUser={currentUser} />

  renderPasswordUpdateSuccess = routeProps => (
    <ProfileUpdateSuccess
      {...routeProps}
      title="Votre mot de passe"
    />
  )

  renderPasswordEditForm = routeProps => {
    const { currentUser, history } = this.props

    return (
      <EditPasswordContainer
        history={history}
        pathToProfile="/profil"
        snackbar={snackbar}
        user={currentUser}
        {...routeProps}
      />
    )
  }

  renderPersonalInformationsEdition = routeProps => {
    const { currentUser, history } = this.props

    return (
      <PersonalInformationsContainer
        getDepartment={getDepartment}
        history={history}
        pathToProfile="/profil"
        snackbar={snackbar}
        user={currentUser}
        {...routeProps}
      />
    )
  }

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
              path="/profil/:view(mot-de-passe)/success/:menu(menu)?"
              render={this.renderPasswordUpdateSuccess}
            />
            <Route
              exact
              key="route-profile-edit-form"
              path="/profil/:view(mot-de-passe)/:menu(menu)?"
              render={this.renderPasswordEditForm}
            />
            <Route
              exact
              key="route-profile-edit-personal-informations"
              path="/profil/:view(informations)/:menu(menu)?"
              render={this.renderPersonalInformationsEdition}
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
  history: PropTypes.shape().isRequired,
  location: PropTypes.shape().isRequired,
}

export default Profile
