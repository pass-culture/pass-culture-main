import React from 'react'
import { connect } from 'react-redux'
import { withRouter } from 'react-router-dom'
import { Route, Switch } from 'react-router-dom/umd/react-router-dom'
import { compose } from 'redux'

import SignupForm from './SignupForm'
import SignupConfirmation from './SignupConfirmation'
import { withRedirectToOffersWhenAlreadyAuthenticated } from '../../hocs'
import Logo from '../../layout/Logo'
import Main from '../../layout/Main'

const SignupPage = ({ location }) => {
  return (
    <Main
      fullscreen
      name="sign-up"
    >
      <div className="logo-side">
        <Logo
          noLink
          signPage
        />
      </div>
      <div className="container">
        <div className="columns">
          <div className="column is-offset-6 is-two-fifths">
            <Switch location={location}>
              <Route
                component={SignupForm}
                exact
                path="/inscription"
              />
              <Route
                component={SignupConfirmation}
                path="/inscription/confirmation"
              />
            </Switch>
          </div>
        </div>
      </div>
    </Main>
  )
}

export default compose(
  withRedirectToOffersWhenAlreadyAuthenticated,
  withRouter,
  connect()
)(SignupPage)
