import React, { useEffect } from 'react'
import { NavLink, Outlet, useLocation } from 'react-router-dom'

import { AppLayout } from 'app/AppLayout'
import { SignupJourneyFormLayout } from 'components/SignupJourneyFormLayout'
import { SignupJourneyContextProvider } from 'context/SignupJourneyContext'
import { Events } from 'core/FirebaseEvents/constants'
import useAnalytics from 'hooks/useAnalytics'
import fullLogoutIcon from 'icons/full-logout.svg'
import logoPassCultureProIcon from 'icons/logo-pass-culture-pro.svg'
import { SvgIcon } from 'ui-kit/SvgIcon/SvgIcon'

import styles from './SignupJourney.module.scss'

export const SignupJourneyRoutes = () => {
  const { logEvent } = useAnalytics()
  const location = useLocation()

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
      <AppLayout
        pageName="sign-up-journey"
        className={styles['sign-up-journey']}
        layout="funnel"
      >
        <header className={styles['header']}>
          <div className={styles['header-content']}>
            <SvgIcon
              className={styles['header-logo']}
              alt="Pass Culture pro, l’espace des acteurs culturels"
              src={logoPassCultureProIcon}
              viewBox="0 0 119 40"
            />
            <NavLink
              onClick={() =>
                logEvent?.(Events.CLICKED_LOGOUT, { from: location.pathname })
              }
              to={`${location.pathname}?logout}`}
              className={styles['logout-link']}
            >
              <SvgIcon
                className="nav-item-icon"
                src={fullLogoutIcon}
                alt=""
                width="20"
              />
              Se déconnecter
            </NavLink>
          </div>
        </header>
        <SignupJourneyContextProvider>
          <SignupJourneyFormLayout>
            <Outlet />
          </SignupJourneyFormLayout>
        </SignupJourneyContextProvider>
      </AppLayout>
    </>
  )
}

// Lazy-loaded by react-router-dom
// ts-unused-exports:disable-next-line
export const Component = SignupJourneyRoutes
