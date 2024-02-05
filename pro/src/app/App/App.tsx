import { setUser as setSentryUser } from '@sentry/browser'
import { useEffect, useState } from 'react'
import { useDispatch } from 'react-redux'
import { Navigate, Outlet, useLocation } from 'react-router-dom'

import { api } from 'apiClient/api'
import { findCurrentRoute } from 'app/AppRouter/findCurrentRoute'
import Notification from 'components/Notification/Notification'
import useActiveFeature from 'hooks/useActiveFeature'
import { useConfigureFirebase } from 'hooks/useAnalytics'
import useCurrentUser from 'hooks/useCurrentUser'
import useFocus from 'hooks/useFocus'
import useLogNavigation from 'hooks/useLogNavigation'
import usePageTitle from 'hooks/usePageTitle'
import { updateUser } from 'store/user/reducer'
import { Consents, initCookieConsent } from 'utils/cookieConsentModal'

import { useLoadFeatureFlags } from './hook/useLoadFeatureFlags'

window.beamer_config = { product_id: 'vjbiYuMS52566', lazy: true }

const App = (): JSX.Element | null => {
  const isBeamerEnabled = useActiveFeature('ENABLE_BEAMER')
  const location = useLocation()
  const { currentUser } = useCurrentUser()
  const [consentedToFirebase, setConsentedToFirebase] = useState(false)
  const [consentedToBeamer, setConsentedToBeamer] = useState(false)
  const dispatch = useDispatch()

  useEffect(() => {
    // Initialize cookie consent modal
    if (location.pathname.indexOf('/adage-iframe') === -1) {
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

  useConfigureFirebase({
    currentUserId: currentUser?.id.toString(),
    isCookieEnabled: consentedToFirebase,
  })
  usePageTitle()
  useLogNavigation()
  useFocus()
  useLoadFeatureFlags()

  useEffect(() => {
    if (consentedToBeamer && currentUser !== null) {
      // We use setTimeout because Beamer might not be loaded yet
      setTimeout(() => {
        if (
          window.Beamer !== undefined &&
          location.pathname.indexOf('/parcours-inscription') === -1 &&
          isBeamerEnabled
        ) {
          window.Beamer.update({ user_id: currentUser.id.toString() })
          window.Beamer.init()
        }
      }, 1000)
    } else {
      window.Beamer?.destroy()
    }
  }, [currentUser, consentedToBeamer])

  useEffect(() => {
    if (currentUser !== null) {
      setSentryUser({ id: currentUser.id.toString() })
    }
  }, [currentUser])

  useEffect(() => {
    if (location.search.includes('logout')) {
      // eslint-disable-next-line @typescript-eslint/no-floating-promises
      api.signout()
      dispatch(updateUser(null))
    }
  }, [location])

  const currentRoute = findCurrentRoute(location)
  if (!currentRoute?.meta?.public && currentUser === null) {
    const fromUrl = encodeURIComponent(`${location.pathname}${location.search}`)
    const loginUrl = fromUrl.includes('logout')
      ? '/connexion'
      : `/connexion?de=${fromUrl}`

    return <Navigate to={loginUrl} replace />
  }

  return (
    <>
      <Outlet />
      <Notification />
    </>
  )
}

export default App
