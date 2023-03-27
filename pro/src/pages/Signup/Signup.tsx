import React, { useEffect } from 'react'
import { Routes, Route } from 'react-router-dom'

import AppLayout from 'app/AppLayout'
import { IRoute } from 'app/AppRouter/routesMap'
import { routesSignup } from 'app/AppRouter/subroutesSignupMap'
import PageTitle from 'components/PageTitle/PageTitle'
import SkipLinks from 'components/SkipLinks'
import useActiveFeature from 'hooks/useActiveFeature'
import { campaignTracker } from 'tracking/mediaCampaignsTracking'
import Logo from 'ui-kit/Logo/Logo'

import styles from './Signup.module.scss'
import SignupUnavailable from './SignupUnavailable/SignupUnavailable'

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
              {routesSignup.map(({ path, element }: IRoute) => (
                <Route key={path} path={path} element={element} />
              ))}
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
