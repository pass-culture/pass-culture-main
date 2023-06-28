import React, { useEffect } from 'react'
import { Route, Routes, useLocation, useNavigate } from 'react-router-dom'

import AppLayout from 'app/AppLayout'
import { routesSignupJourney } from 'app/AppRouter/subroutesSignupJourneyMap'
import { SignupJourneyFormLayout } from 'components/SignupJourneyFormLayout'
import SkipLinks from 'components/SkipLinks'
import { SignupJourneyContextProvider } from 'context/SignupJourneyContext'
import { Events } from 'core/FirebaseEvents/constants'
import useAnalytics from 'hooks/useAnalytics'
import { DisconnectFullIcon } from 'icons'
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

  useEffect(() => {
    if (window.Beamer !== undefined) {
      window.Beamer.hide()
    }

    return () => {
      if (window.Beamer !== undefined) {
        window.Beamer.show()
      }
    }
  }, [])

  return (
    <>
      <SkipLinks displayMenu={false} />
      <header className={styles['header']}>
        <div className={styles['header-content']}>
          <img
            alt="Pass Culture pro, l'espace des acteurs culturels"
            src={`${ROOT_PATH}/icons/brand-logo-pc-purple.png`}
          />
          <Button
            onClick={onSignoutClick}
            variant={ButtonVariant.TERNARY}
            Icon={DisconnectFullIcon}
          >
            Se déconnecter
          </Button>
        </div>
      </header>
      <AppLayout
        layoutConfig={{
          fullscreen: true,
          pageName: 'sign-up-journey',
        }}
        className={styles['sign-up-journey']}
      >
        <SignupJourneyContextProvider>
          <SignupJourneyFormLayout>
            <Routes>
              {routesSignupJourney.map(({ path, element }) => (
                <Route key={path} path={path} element={element} />
              ))}
            </Routes>
          </SignupJourneyFormLayout>
        </SignupJourneyContextProvider>
      </AppLayout>
    </>
  )
}

export default SignupJourneyRoutes
