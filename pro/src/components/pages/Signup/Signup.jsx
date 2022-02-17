import PropTypes from 'prop-types'
import React, { useEffect } from 'react'
import { Route, Switch } from 'react-router-dom'

import AppLayout from 'app/AppLayout'
import useActiveFeature from 'components/hooks/useActiveFeature'
import Logo from 'components/layout/Logo'
import PageTitle from 'components/layout/PageTitle/PageTitle'
import { campaignTracker } from 'tracking/mediaCampaignsTracking'

import SignupConfirmationContainer from './SignupConfirmation/SignupConfirmationContainer'
import SignupFormContainer from './SignupForm/SignupFormContainer'
import SignupUnavailable from './SignupUnavailable/SignupUnavailable'

const Signup = ({ location }) => {
  useEffect(() => {
    campaignTracker.signUp()
  }, [])
  const isProAccountCreationEnabled = useActiveFeature(
    'ENABLE_PRO_ACCOUNT_CREATION'
  )
  return (
    <AppLayout
      layoutConfig={{
        fullscreen: true,
        pageName: 'sign-up',
      }}
    >
      <PageTitle title="S’inscrire" />
      <div className="logo-side">
        <Logo noLink signPage />
      </div>
      {isProAccountCreationEnabled ? (
        <Switch location={location}>
          <Route component={SignupFormContainer} exact path="/inscription" />
          <Route
            component={SignupConfirmationContainer}
            path="/inscription/confirmation"
          />
        </Switch>
      ) : (
        <SignupUnavailable />
      )}
    </AppLayout>
  )
}

Signup.propTypes = {
  location: PropTypes.shape().isRequired,
}

export default Signup
