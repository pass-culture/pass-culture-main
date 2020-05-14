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
import User from './ValueObjects/User'

export const getDepartment = departmentCode => {
  const departmentName = getDepartementByCode(departmentCode)
  return `${departmentName} (${departmentCode})`
}

class Profile extends PureComponent {
  renderProfileMainView = (user, history) => () => (
    <ProfileMainView
      historyPush={history.push}
      user={user}
    />
  )

  renderPasswordEditForm = routeProps => {
    const { user, history } = this.props

    return (
      <EditPasswordContainer
        history={history}
        pathToProfile="/profil"
        snackbar={snackbar}
        user={user}
        {...routeProps}
      />
    )
  }

  renderPersonalInformationsEdition = routeProps => {
    const { user, history } = this.props

    return (
      <PersonalInformationsContainer
        getDepartment={getDepartment}
        history={history}
        pathToProfile="/profil"
        snackbar={snackbar}
        user={user}
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
    const { user, history, location } = this.props

    return (
      <div
        className="page is-relative"
        id="profile-page"
      >
        {user && (
          <Switch location={location}>
            <Route
              exact
              key="route-profile-main-view"
              path="/profil/:menu(menu)?"
              render={this.renderProfileMainView(user, history)}
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
