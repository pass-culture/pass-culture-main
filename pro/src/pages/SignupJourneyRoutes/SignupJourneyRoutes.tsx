import React from 'react'
import { Route, Routes, useLocation, useNavigate } from 'react-router-dom'

import AppLayout from 'app/AppLayout'
import { SignupJourneyFormLayout } from 'components/SignupJourneyFormLayout'
import { SignupJourneyContextProvider } from 'context/SignupJourneyContext'
import { Events } from 'core/FirebaseEvents/constants'
import useAnalytics from 'hooks/useAnalytics'
import { ExitIcon } from 'icons'
import { Activity } from 'screens/SignupJourneyForm/Activity'
import { OffererAuthentication } from 'screens/SignupJourneyForm/Authentication'
import { ConfirmedAttachment } from 'screens/SignupJourneyForm/ConfirmedAttachment'
import { Offerer } from 'screens/SignupJourneyForm/Offerer'
import { Offerers } from 'screens/SignupJourneyForm/Offerers'
import { Validation } from 'screens/SignupJourneyForm/Validation'
import { Welcome } from 'screens/SignupJourneyForm/Welcome'
import { Button } from 'ui-kit'
import { ButtonVariant } from 'ui-kit/Button/types'
import { ROOT_PATH } from 'utils/config'

import styles from './SignupJourney.module.scss'

const SignupJourneyRoutes = () => {
  const { logEvent } = useAnalytics()
  const location = useLocation()
  const navigate = useNavigate()
  const onSignoutClick = () => {
    logEvent?.(Events.CLICKED_LOGOUT, { from: location.pathname })
    navigate('/logout')
  }

  return (
    <AppLayout
      layoutConfig={{
        fullscreen: true,
        pageName: 'sign-up-journey',
      }}
      className={styles['sign-up-journey']}
    >
      <header className={styles['header']}>
        <div className={styles['header-content']}>
          <img
            alt="Pass Culture pro, l'espace Pass Culture des acteurs culturels"
            src={`${ROOT_PATH}/icons/brand-logo-pc-purple.png`}
          />
          <Button
            onClick={onSignoutClick}
            variant={ButtonVariant.TERNARY}
            Icon={ExitIcon}
          >
            Se déconnecter
          </Button>
        </div>
      </header>
      <SignupJourneyContextProvider>
        <SignupJourneyFormLayout>
          <Routes>
            <Route path="/" element={<Welcome />} />
            <Route path="/structure" element={<Offerer />} />
            <Route path="/structure/rattachement" element={<Offerers />} />
            <Route
              path="/structure/rattachement/confirmation"
              element={<ConfirmedAttachment />}
            />
            <Route
              path="/authentification"
              element={<OffererAuthentication />}
            />
            <Route path="/activite" element={<Activity />} />
            <Route path="/validation" element={<Validation />} />
          </Routes>
        </SignupJourneyFormLayout>
      </SignupJourneyContextProvider>
    </AppLayout>
  )
}

export default SignupJourneyRoutes
