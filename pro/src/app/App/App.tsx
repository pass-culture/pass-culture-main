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
  const [isCookieConsentChecked, setIsCookieConsentChecked] = useState(false)

  // Initialize cookie consent modal
  if (!isCookieConsentChecked) {
    setTimeout(() => {
      if (
        isCookieBannerEnabled &&
        location.pathname.indexOf('/adage-iframe') === -1
      ) {
        const orejime = initCookieConsent()
        // Set the consent on consent change
        orejime.internals.manager.watch({
          update: ({
            consents,
          }: {
            consents: { [key in Consents]: boolean }
          }) => {
            setConsentedToFirebase(consents.firebase)
            setConsentedToBeamer(consents.beamer)
          },
        })
        // Set the consent if the user has already seen the modal
        setConsentedToFirebase(
          orejime.internals.manager.consents[Consents.FIREBASE]
        )
        setConsentedToBeamer(
          orejime.internals.manager.consents[Consents.BEAMER]
        )
      } else {
        setConsentedToFirebase(true)
        setConsentedToBeamer(true)
      }
    })
    setIsCookieConsentChecked(true)
  }

  const isMaintenanceActivated = useSelector(maintenanceSelector)
  useConfigureFirebase({
    currentUserId: currentUser?.nonHumanizedId.toString(),
    isCookieEnabled: consentedToFirebase,
  })
  usePageTitle()
  useLogNavigation()

  useEffect(() => {
    if (
      consentedToBeamer &&
      currentUser !== null &&
      window.Beamer !== undefined
    ) {
      window.Beamer.update({
        user_firstname: currentUser.firstName,
        user_lastname: currentUser.lastName,
        user_email: currentUser.email,
        user_id: currentUser.nonHumanizedId.toString(),
      })
      window.Beamer.init()
    }
  }, [currentUser, consentedToBeamer])

  if (currentUser !== null) {
    setSentryUser({ id: currentUser.nonHumanizedId.toString() })
  }

  if (isMaintenanceActivated) {
    window.location.href = URL_FOR_MAINTENANCE
    return null
  }

  return (
    <>
      {children}
      <Notification />
    </>
  )
}

export default App
