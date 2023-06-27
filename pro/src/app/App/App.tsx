import { setUser as setSentryUser } from '@sentry/browser'
import React, { useEffect, useState } from 'react'
import { useSelector } from 'react-redux'
import { useLocation } from 'react-router-dom'

import Notification from 'components/Notification/Notification'
import useActiveFeature from 'hooks/useActiveFeature'
import { useConfigureFirebase } from 'hooks/useAnalytics'
import useCurrentUser from 'hooks/useCurrentUser'
import useLogNavigation from 'hooks/useLogNavigation'
import usePageTitle from 'hooks/usePageTitle'
import { maintenanceSelector } from 'store/selectors/maintenanceSelector'
import { URL_FOR_MAINTENANCE } from 'utils/config'
import { Consents, initCookieConsent } from 'utils/cookieConsentModal'

interface AppProps {
  children: JSX.Element
}

const App = ({ children }: AppProps): JSX.Element | null => {
  const isCookieBannerEnabled = useActiveFeature('WIP_ENABLE_COOKIES_BANNER')
  const location = useLocation()
  const { currentUser } = useCurrentUser()
  const [consentedToFirebase, setConsentedToFirebase] = useState(false)
  const [consentedToBeamer, setConsentedToBeamer] = useState(false)

  useEffect(() => {
    // Initialize cookie consent modal
    if (
      isCookieBannerEnabled &&
      location.pathname.indexOf('/adage-iframe') === -1
    ) {
      setTimeout(() => {
        const orejime = initCookieConsent()
        // Set the consent on consent change
        orejime.internals.manager.watch({
          update: ({
            consents,
          }: {
            consents: { [key in Consents]: boolean }
          }) => {
            setConsentedToFirebase(consents[Consents.FIREBASE])
            setConsentedToBeamer(consents[Consents.BEAMER])
          },
        })
        setConsentedToFirebase(
          orejime.internals.manager.consents[Consents.FIREBASE]
        )
        setConsentedToBeamer(
          orejime.internals.manager.consents[Consents.BEAMER]
        )

        // We force the banner to be displayed again if the cookie was deleted somehow
        if (!document.cookie.includes('orejime')) {
          orejime.internals.manager.confirmed = false
          initCookieConsent()
        }
      })
    } else {
      setConsentedToFirebase(true)
      setConsentedToBeamer(true)
    }
  }, [location.pathname])

  const isMaintenanceActivated = useSelector(maintenanceSelector)
  useConfigureFirebase({
    currentUserId: currentUser?.nonHumanizedId.toString(),
    isCookieEnabled: consentedToFirebase,
  })
  usePageTitle()
  useLogNavigation()

  useEffect(() => {
    if (consentedToBeamer && currentUser !== null) {
      // We use setTimeout because Beamer might not be loaded yet
      setTimeout(() => {
        if (window.Beamer !== undefined) {
          window.Beamer.update({
            user_firstname: currentUser.firstName,
            user_lastname: currentUser.lastName,
            user_email: currentUser.email,
            user_id: currentUser.nonHumanizedId.toString(),
          })
          window.Beamer.init()
        }
      }, 1000)
    } else {
      window.Beamer?.destroy()
    }
  }, [currentUser, consentedToBeamer])

  useEffect(() => {
    if (currentUser !== null) {
      setSentryUser({ id: currentUser.nonHumanizedId.toString() })
    }
  }, [currentUser])

  useEffect(() => {
    if (isMaintenanceActivated) {
      window.location.href = URL_FOR_MAINTENANCE
    }
  }, [isMaintenanceActivated])

  if (isMaintenanceActivated) return null
  return (
    <>
      {children}
      <Notification />
    </>
  )
}

export default App
