/* eslint
  react/jsx-one-expression-per-line: 0 */
import React from 'react'
import { compose } from 'redux'
import PropTypes from 'prop-types'
import { connect } from 'react-redux'
import { withLogin } from 'pass-culture-shared'
import PageTransition from 'react-router-page-transition'
import { Route, Switch, withRouter } from 'react-router-dom'

import Loader from '../layout/Loader'
import ProfileEditView from '../profile/views/ProfileEditView'
import ProfileMainView from '../profile/views/ProfileMainView'

const ProfilePage = ({ user, location }) => {
  const isloaded = user || typeof user === 'object'
  return (
    <div id="profile-page" className="page is-relative">
      {isloaded && (
        <PageTransition timeout={500}>
          <Switch location={location}>
            <Route
              exact
              path="/profil"
              component={ProfileMainView}
              key="route-profile-main-view"
            />
            <Route
              exact
              path="/profil/:view"
              component={ProfileEditView}
              key="route-profile-edit-view"
            />
          </Switch>
        </PageTransition>
      )}
      <Loader isloading={!isloaded} />
    </div>
  )
}

ProfilePage.propTypes = {
  location: PropTypes.object.isRequired,
  user: PropTypes.oneOfType([PropTypes.bool, PropTypes.object]).isRequired,
}

const mapStateToProps = state => {
  const user = state.user || false
  return { user }
}

export default compose(
  withRouter,
  withLogin({ failRedirect: '/connexion' }),
  connect(mapStateToProps)
)(ProfilePage)
