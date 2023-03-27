import React, { useEffect } from 'react'
import { Routes, Route } from 'react-router-dom'

import AppLayout from 'app/AppLayout'
import PageTitle from 'components/PageTitle/PageTitle'
import SkipLinks from 'components/SkipLinks'
import useActiveFeature from 'hooks/useActiveFeature'
import { campaignTracker } from 'tracking/mediaCampaignsTracking'
import Logo from 'ui-kit/Logo/Logo'

import styles from './Signup.module.scss'
import SignupConfirmation from './SignupConfirmation/SignupConfirmation'
import SignupContainer from './SignupContainer/SignupContainer'
import SignupUnavailable from './SignupUnavailable/SignupUnavailable'
import SignUpValidation from './SignUpValidation'

const Signup = () => {
  useEffect(() => {
    campaignTracker.signUp()
  }, [])
  const isProAccountCreationEnabled = useActiveFeature(
    'ENABLE_PRO_ACCOUNT_CREATION'
  )
  return (
    <>
      <SkipLinks displayMenu={false} />
      <div className={styles['sign-up']}>
        <header className={styles['logo-side']}>
          <Logo noLink signPage />
        </header>
        <AppLayout
          layoutConfig={{
            fullscreen: true,
            pageName: 'sign-up',
          }}
        >
          <PageTitle title="S’inscrire" />

          {isProAccountCreationEnabled ? (
            <Routes>
              <Route element={<SignupContainer />} path="" />
              <Route element={<SignupConfirmation />} path="/confirmation" />
              <Route element={<SignUpValidation />} path="/validation/:token" />
            </Routes>
          ) : (
            <SignupUnavailable />
          )}
        </AppLayout>
      </div>
    </>
  )
}

export default Signup
