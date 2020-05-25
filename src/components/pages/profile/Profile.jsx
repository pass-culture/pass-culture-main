import PropTypes from 'prop-types'
import React, { PureComponent } from 'react'
import { Route, Switch } from 'react-router-dom'

import { snackbar } from '../../../utils/snackbar'
import { getDepartment } from './utils/utils'
import LoaderContainer from '../../layout/Loader/LoaderContainer'
import EditPasswordContainer from './EditPassword/EditPasswordContainer'
import LegalNotice from './LegalNotice/LegalNotice'
import PersonalInformationsContainer from './PersonalInformations/PersonalInformationsContainer'
import MainView from './MainView/MainView'
import User from './ValueObjects/User'

class Profile extends PureComponent {
  render() {
    const { user, history, location } = this.props
    const pathToProfile = '/profil'
    const { email, id, departmentCode } = user
    const department = getDepartment(departmentCode)

    return (
      <div className="page profile-page">
        {user && (
          <Switch location={location}>
            <Route
              exact
              key="route-profile-main-view"
              path="/profil/:menu(menu)?"
            >
              <MainView
                historyPush={history.push}
                user={user}
              />
            </Route>
            <Route
              exact
              key="route-profile-edit-form"
              path="/profil/:view(mot-de-passe)/:menu(menu)?"
            >
              <EditPasswordContainer
                historyPush={history.push}
                pathToProfile={pathToProfile}
                snackbar={snackbar}
                user={user}
                {...this.props}
              />
            </Route>
            <Route
              exact
              key="route-profile-edit-personal-informations"
              path="/profil/:view(informations)/:menu(menu)?"
            >
              <PersonalInformationsContainer
                department={department}
                historyPush={history.push}
                pathToProfile={pathToProfile}
                snackbar={snackbar}
                user={user}
              />
            </Route>
            <Route
              exact
              key="route-legal-notice"
              path="/profil/:view(mentions-legales)/:menu(menu)?"
            >
              <LegalNotice
                historyPush={history.push}
                pathToProfile={pathToProfile}
                userEmail={email}
                userId={id}
              />
            </Route>
          </Switch>
        )}
        {!user && <LoaderContainer isLoading />}
      </div>
    )
  }
}

Profile.propTypes = {
  history: PropTypes.shape().isRequired,
  location: PropTypes.shape().isRequired,
  user: PropTypes.instanceOf(User).isRequired,
}

export default Profile
