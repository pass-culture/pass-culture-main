import React, { useEffect } from 'react'
import { Route, Routes, useLocation } from 'react-router-dom'

import AppLayout from 'app/AppLayout'
import { routesSignupJourney } from 'app/AppRouter/subroutesSignupJourneyMap'
import { SignupJourneyFormLayout } from 'components/SignupJourneyFormLayout'
import SkipLinks from 'components/SkipLinks'
import { SignupJourneyContextProvider } from 'context/SignupJourneyContext'
import { Events } from 'core/FirebaseEvents/constants'
import useAnalytics from 'hooks/useAnalytics'
import { useLogout } from 'hooks/useLogout'
import fullLogoutIcon from 'icons/full-logout.svg'
import logoPassCultureProIcon from 'icons/logo-pass-culture-pro.svg'
import { Button } from 'ui-kit'
import { ButtonVariant } from 'ui-kit/Button/types'
import { SvgIcon } from 'ui-kit/SvgIcon/SvgIcon'

import styles from './SignupJourney.module.scss'

const SignupJourneyRoutes = () => {
  const { logEvent } = useAnalytics()
  const location = useLocation()
  const logout = useLogout()

  const onSignoutClick = async () => {
    logEvent?.(Events.CLICKED_LOGOUT, { from: location.pathname })
    await logout()
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
          <SvgIcon
            className={styles['header-logo']}
            alt="Pass Culture pro, l’espace des acteurs culturels"
            src={logoPassCultureProIcon}
            viewBox="0 0 119 40"
          />
          <Button
            onClick={onSignoutClick}
            variant={ButtonVariant.TERNARY}
            icon={fullLogoutIcon}
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
