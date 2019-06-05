/* eslint
  react/jsx-one-expression-per-line: 0 */
import React from 'react'
import { compose } from 'redux'
import PropTypes from 'prop-types'
import { connect } from 'react-redux'
import { Route, Switch } from 'react-router-dom'

import { config } from './config'
import NotMatch from '../NotMatch'
import { withRedirectToSigninOrTypeformAfterLogin } from '../../hocs'
import { Loader } from '../../layout/Loader'
import ProfileMainView from './ProfileMainView'
import ProfileUpdateSuccess from './ProfileUpdateSuccess'

const parseRoutesWithComponent = () => {
  const components = config.filter(o => o.component)
  const routes = components.reduce(
    (acc, o) => ({ ...acc, [o.routeName]: o }),
    {}
  )
  return routes
}

const ProfilePage = ({ currentUser, isCurrentUserLoaded, location }) => {
  const routes = parseRoutesWithComponent()
  const possibleRoutes = Object.keys(routes).join('|')
  return (
    <div id="profile-page" className="page is-relative">
      {isCurrentUserLoaded && (
        <Switch location={location}>
          <Route
            exact
            path="/profil/:menu(menu)?"
            key="route-profile-main-view"
            render={() => (
              <ProfileMainView currentUser={currentUser} config={config} />
            )}
          />
          <Route
            exact
            path={`/profil/:view(${possibleRoutes})/success/:menu(menu)?`}
            key="route-profile-update-success"
            render={routeProps => (
              <ProfileUpdateSuccess {...routeProps} config={routes} />
            )}
          />
          <Route
            exact
            path={`/profil/:view(${possibleRoutes})/:menu(menu)?`}
            key="route-profile-edit-form"
            render={routeProps => {
              const { view } = routeProps.match.params
              const Component = routes[view].component
              if (!Component) return null
              const { title } = routes[view]
              return <Component {...routeProps} title={title} />
            }}
          />
          <Route
            component={routeProps => (
              <NotMatch {...routeProps} delay={3} redirect="/profil" />
            )}
          />
        </Switch>
      )}
      {!isCurrentUserLoaded && <Loader isLoading />}
    </div>
  )
}

ProfilePage.propTypes = {
  currentUser: PropTypes.object.isRequired,
  isCurrentUserLoaded: PropTypes.bool.isRequired,
  location: PropTypes.object.isRequired,
}

const mapStateToProps = (state, ownProps) => {
  const currentUser = ownProps.currentUser || false
  const isCurrentUserLoaded =
    (currentUser && currentUser !== null) || typeof currentUser === 'object'
  return {
    isCurrentUserLoaded,
  }
}

export default compose(
  withRedirectToSigninOrTypeformAfterLogin,
  connect(mapStateToProps)
)(ProfilePage)
