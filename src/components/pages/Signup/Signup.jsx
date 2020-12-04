import PropTypes from 'prop-types'
import React, { useEffect } from 'react'
import { Route, Switch } from 'react-router-dom/umd/react-router-dom'

import AppLayout from 'app/AppLayout'
import Logo from 'components/layout/Logo'
import PageTitle from 'components/layout/PageTitle/PageTitle'
import { campaignTracker } from 'tracking/mediaCampaignsTracking'

import SignupConfirmationContainer from './SignupConfirmation/SignupConfirmationContainer'
import SignupFormContainer from './SignupForm/SignupFormContainer'

const Signup = ({ location }) => {
  useEffect(() => {
    campaignTracker.signUp()
  }, [])

  return (
    <AppLayout
      layoutConfig={{
        fullscreen: true,
        pageName: 'sign-up',
      }}
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
    </AppLayout>
  )
}

Signup.propTypes = {
  location: PropTypes.shape().isRequired,
}

export default Signup
