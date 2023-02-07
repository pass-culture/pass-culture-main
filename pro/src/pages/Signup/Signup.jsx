import PropTypes from 'prop-types'
import React, { useEffect } from 'react'
import { Route, Switch } from 'react-router-dom'

import AppLayout from 'app/AppLayout'
import { subRoutesInscription } from 'app/AppRouter/routes_map'
import useActiveFeature from 'hooks/useActiveFeature'
import { campaignTracker } from 'tracking/mediaCampaignsTracking'
import Logo from 'ui-kit/Logo/Logo'

import styles from './Signup.module.scss'
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
      className={styles['sign-up']}
    >
      <div className={styles['logo-side']}>
        <Logo noLink signPage />
      </div>
      {isProAccountCreationEnabled ? (
        <Switch location={location}>
          {subRoutesInscription.map(route => (
            <Route
              exact={route.exact}
              key={
                Array.isArray(route.path) ? route.path.join('|') : route.path
              }
              path={route.path}
            >
              <route.component />
            </Route>
          ))}
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
