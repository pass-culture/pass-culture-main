import PropTypes from 'prop-types'
import React from 'react'
import { Route, Switch } from 'react-router-dom/umd/react-router-dom'

import Logo from 'components/layout/Logo'
import Main from 'components/layout/Main'
import PageTitle from 'components/layout/PageTitle/PageTitle'

import SignupConfirmationContainer from './SignupConfirmation/SignupConfirmationContainer'
import SignupFormContainer from './SignupForm/SignupFormContainer'

const Signup = ({ location }) => {
  return (
    <Main
      fullscreen
      name="sign-up"
    >
      <PageTitle title="S’inscrire" />
      <div className="logo-side">
        <Logo
          noLink
          signPage
        />
      </div>
      <div className="container">
        <div className="columns">
          <div className="column is-offset-6 is-two-fifths sign-page-form">
            <Switch location={location}>
              <Route
                component={SignupFormContainer}
                exact
                path="/inscription"
              />
              <Route
                component={SignupConfirmationContainer}
                path="/inscription/confirmation"
              />
            </Switch>
          </div>
        </div>
      </div>
    </Main>
  )
}

Signup.propTypes = {
  location: PropTypes.shape().isRequired,
}

export default Signup
