import React, { useEffect } from 'react'
import { Routes, Route } from 'react-router-dom-v5-compat'

import AppLayout from 'app/AppLayout'
import PageTitle from 'components/PageTitle/PageTitle'
import useActiveFeature from 'hooks/useActiveFeature'
import { campaignTracker } from 'tracking/mediaCampaignsTracking'
import Logo from 'ui-kit/Logo/Logo'

import styles from './Signup.module.scss'
import SignupConfirmation from './SignupConfirmation/SignupConfirmation'
import SignupContainer from './SignupContainer/SignupContainer'
import SignupUnavailable from './SignupUnavailable/SignupUnavailable'

const Signup = () => {
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
      <PageTitle title="S’inscrire" />
      <div className={styles['logo-side']}>
        <Logo noLink signPage />
      </div>
      {isProAccountCreationEnabled ? (
        <Routes>
          <Route element={<SignupContainer />} path="" />
          <Route element={<SignupConfirmation />} path="/confirmation" />
        </Routes>
      ) : (
        <SignupUnavailable />
      )}
    </AppLayout>
  )
}

export default Signup
