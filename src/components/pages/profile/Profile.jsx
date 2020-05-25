import PropTypes from 'prop-types'
import React, { PureComponent } from 'react'
import { Route, Switch } from 'react-router-dom'

import getDepartementByCode from '../../../utils/getDepartementByCode'
import { snackbar } from '../../../utils/snackbar'
import LoaderContainer from '../../layout/Loader/LoaderContainer'
import NotMatch from '../not-match/NotMatch'
import EditPasswordContainer from './EditPassword/EditPasswordContainer'
import LegalNotice from './LegalNotice/LegalNotice'
import PersonalInformationsContainer from './PersonalInformations/PersonalInformationsContainer'
import MainView from './MainView/MainView'
import User from './ValueObjects/User'

export const getDepartment = departmentCode => {
  const departmentName = getDepartementByCode(departmentCode)
  return `${departmentName} (${departmentCode})`
}

class Profile extends PureComponent {
  renderNoMatch = routeProps => (<NotMatch
    delay={3}
    redirect="/profil"
    {...routeProps}
                                 />)

  render() {
    const { user, history, location } = this.props
    const pathToProfile = '/profil'
    const { email, id } = user

    return (
      <div
        className="page is-relative profile-page"
        id="profile-page"
      >
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
                getDepartment={getDepartment}
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
            <Route component={this.renderNoMatch} />
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
