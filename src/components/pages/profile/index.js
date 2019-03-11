/* eslint
  react/jsx-one-expression-per-line: 0 */
import React from 'react'
import { compose } from 'redux'
import PropTypes from 'prop-types'
import { connect } from 'react-redux'
import { withLogin } from 'pass-culture-shared'
import { Route, Switch, withRouter } from 'react-router-dom'

import { config } from './config'
import NotMatch from '../NotMatch'
import Loader from '../../layout/Loader'
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

const ProfilePage = ({ isloaded, location, user }) => {
  const routes = parseRoutesWithComponent()
  const possibleRoutes = Object.keys(routes).join('|')
  return (
    <div id="profile-page" className="page is-relative">
      {isloaded && (
        <Switch location={location}>
          <Route
            exact
            path="/profil/:menu(menu)?"
            key="route-profile-main-view"
            render={() => <ProfileMainView user={user} config={config} />}
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
              return <Component {...routeProps} title={title} user={user} />
            }}
          />
          <Route
            component={routeProps => (
              <NotMatch {...routeProps} delay={3} redirect="/profil" />
            )}
          />
        </Switch>
      )}
      {!isloaded && <Loader isloading />}
    </div>
  )
}

ProfilePage.propTypes = {
  isloaded: PropTypes.bool.isRequired,
  location: PropTypes.object.isRequired,
  user: PropTypes.object.isRequired,
}

const mapStateToProps = state => {
  const user = state.user || false
  const isloaded = (user && user !== null) || typeof user === 'object'
  return { isloaded, user }
}

export default compose(
  withRouter,
  withLogin({ failRedirect: '/connexion' }),
  connect(mapStateToProps)
)(ProfilePage)
