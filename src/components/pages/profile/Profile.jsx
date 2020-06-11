import PropTypes from 'prop-types'
import React, { Fragment } from 'react'
import { Route, Switch } from 'react-router-dom'
import { toast } from 'react-toastify'

import LoaderContainer from '../../layout/Loader/LoaderContainer'
import { getDepartment } from './domain/getDepartment'
import { handleEditPasswordSubmit } from './repository/handleEditPasswordSubmit'
import EditPassword from './EditPassword/EditPassword'
import LegalNotice from './LegalNotice/LegalNotice'
import MainView from './MainView/MainView'
import PersonalInformationsContainer from './PersonalInformations/PersonalInformationsContainer'
import User from './ValueObjects/User'

const Profile = ({ user, history }) => {
  const pathToProfile = '/profil'
  const { email, departmentCode } = user
  const department = getDepartment(departmentCode)

  return (
    <Fragment>
      {user && (
        <Switch>
          <Route path="/profil/mot-de-passe">
            <EditPassword
              handleSubmit={handleEditPasswordSubmit}
              historyPush={history.push}
              pathToProfile={pathToProfile}
              triggerSuccessSnackbar={toast.success}
              user={user}
            />
          </Route>
          <Route path="/profil/informations">
            <PersonalInformationsContainer
              department={department}
              historyPush={history.push}
              pathToProfile={pathToProfile}
              triggerSuccessSnackbar={toast.success}
              user={user}
            />
          </Route>
          <Route path="/profil/mentions-legales">
            <LegalNotice
              historyPush={history.push}
              pathToProfile={pathToProfile}
              userEmail={email}
            />
          </Route>
          <Route path="/profil">
            <MainView
              historyPush={history.push}
              user={user}
            />
          </Route>
        </Switch>
      )}
      {!user && <LoaderContainer isLoading />}
    </Fragment>
  )
}

Profile.propTypes = {
  history: PropTypes.shape().isRequired,
  user: PropTypes.instanceOf(User).isRequired,
}

export default Profile
