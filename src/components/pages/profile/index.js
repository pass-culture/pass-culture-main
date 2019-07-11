import PropTypes from 'prop-types'
import React from 'react'
import { connect } from 'react-redux'
import { Route, Switch } from 'react-router-dom'
import { compose } from 'redux'
import { selectCurrentUser } from 'with-react-redux-login'

import { config } from './config'
import ProfileMainView from './ProfileMainView'
import ProfileUpdateSuccess from './ProfileUpdateSuccess'
import NotMatch from '../NotMatch'
import { withRequiredLogin } from '../../hocs'
import LoaderContainer from '../../layout/Loader/LoaderContainer'

const parseRoutesWithComponent = () => {
  const components = config.filter(o => o.component)
  const routes = components.reduce(
    (acc, o) => ({ ...acc, [o.routeName]: o }),
    {}
  )
  return routes
}

const ProfilePage = ({ currentUser, location }) => {
  const routes = parseRoutesWithComponent()
  const possibleRoutes = Object.keys(routes).join('|')

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
            render={() => (
              <ProfileMainView
                config={config}
                currentUser={currentUser}
              />
            )}
          />
          <Route
            exact
            key="route-profile-update-success"
            path={`/profil/:view(${possibleRoutes})/success/:menu(menu)?`}
            render={routeProps => (
              <ProfileUpdateSuccess
                {...routeProps}
                config={routes}
              />
            )}
          />
          <Route
            exact
            key="route-profile-edit-form"
            path={`/profil/:view(${possibleRoutes})/:menu(menu)?`}
            render={routeProps => {
              const { view } = routeProps.match.params
              const Component = routes[view].component
              if (!Component) return null
              const { title } = routes[view]
              return (<Component
                {...routeProps}
                title={title}
                      />)
            }}
          />
          <Route
            component={routeProps => (
              <NotMatch
                {...routeProps}
                delay={3}
                redirect="/profil"
              />
            )}
          />
        </Switch>
      )}
      {!currentUser && <LoaderContainer isLoading />}
    </div>
  )
}

ProfilePage.propTypes = {
  currentUser: PropTypes.shape().isRequired,
  location: PropTypes.shape().isRequired,
}

const mapStateToProps = state => ({
  currentUser: selectCurrentUser(state),
})

export default compose(
  withRequiredLogin,
  connect(mapStateToProps)
)(ProfilePage)
