import PropTypes from 'prop-types'
import React from 'react'
import { Route, Switch } from 'react-router-dom'
import { toast } from 'react-toastify'

import LoaderContainer from '../../layout/Loader/LoaderContainer'
import { getDepartment } from './domain/getDepartment'
import EditPasswordContainer from './EditPassword/EditPasswordContainer'
import LegalNotice from './LegalNotice/LegalNotice'
import MainView from './MainView/MainView'
import PersonalInformationsContainer from './PersonalInformations/PersonalInformationsContainer'
import User from './ValueObjects/User'

const Profile = ({ user, history, location }) => {
  const pathToProfile = '/profil'
  const { email, departmentCode } = user
  const department = getDepartment(departmentCode)

  return (
    <div className="page profile-page">
      {user && (
        <Switch location={location}>
          <Route
            exact
            key="route-profile-main-view"
            path="/profil"
          >
            <MainView
              historyPush={history.push}
              user={user}
            />
          </Route>
          <Route
            exact
            key="route-profile-edit-form"
            path="/profil/:view(mot-de-passe)"
          >
            <EditPasswordContainer
              historyPush={history.push}
              pathToProfile={pathToProfile}
              triggerSuccessSnackbar={toast.success}
              user={user}
            />
          </Route>
          <Route
            exact
            key="route-profile-edit-personal-informations"
            path="/profil/:view(informations)"
          >
            <PersonalInformationsContainer
              department={department}
              historyPush={history.push}
              pathToProfile={pathToProfile}
              triggerSuccessSnackbar={toast.success}
              user={user}
            />
          </Route>
          <Route
            exact
            key="route-legal-notice"
            path="/profil/:view(mentions-legales)"
          >
            <LegalNotice
              historyPush={history.push}
              pathToProfile={pathToProfile}
              userEmail={email}
            />
          </Route>
        </Switch>
      )}
      {!user && <LoaderContainer isLoading />}
    </div>
  )
}

Profile.propTypes = {
  history: PropTypes.shape().isRequired,
  location: PropTypes.shape().isRequired,
  user: PropTypes.instanceOf(User).isRequired,
}

export default Profile
