import { setUser as setSentryUser } from '@sentry/browser'
import React, { useState } from 'react'
import { useSelector } from 'react-redux'
import { useLocation } from 'react-router-dom'

import Notification from 'components/Notification/Notification'
import { useConfigureFirebase } from 'hooks/useAnalytics'
import useCurrentUser from 'hooks/useCurrentUser'
import useLogNavigation from 'hooks/useLogNavigation'
import usePageTitle from 'hooks/usePageTitle'
import { maintenanceSelector } from 'store/selectors/maintenanceSelector'
import { URL_FOR_MAINTENANCE } from 'utils/config'
import { initCookieConsent } from 'utils/cookieConsentModal'

interface AppProps {
  children: JSX.Element
}

const App = ({ children }: AppProps): JSX.Element | null => {
  const location = useLocation()
  const { currentUser } = useCurrentUser()
  const [consentedToFirebase, setConsentedToFirebase] = useState(false)
  const [isCookieConsentChecked, setIsCookieConsentChecked] = useState(false)

  // Initialize cookie consent modal
  if (!isCookieConsentChecked) {
    setTimeout(() => {
      if (
        process.env.REACT_APP_ENVIRONMENT_NAME !== 'production' &&
        location.pathname.indexOf('/adage-iframe') === -1
      ) {
        const orejime = initCookieConsent()
        // Set the consent on consent change
        orejime.internals.manager.watch({
          update: ({ consents }: { consents: { firebase: boolean } }) => {
            setConsentedToFirebase(consents.firebase)
          },
        })
        // Set the consent if the user has already seen the modal
        setConsentedToFirebase(orejime.internals.manager.consents['firebase'])
      } else {
        setConsentedToFirebase(true)
      }
    })
    setIsCookieConsentChecked(true)
  }

  const isMaintenanceActivated = useSelector(maintenanceSelector)
  useConfigureFirebase({
    currentUserId: currentUser?.nonHumanizedId,
    isCookieEnabled: consentedToFirebase,
  })
  usePageTitle()
  useLogNavigation()

  if (currentUser !== null) {
    setSentryUser({ id: currentUser.id })
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
