import React, { useEffect } from 'react'
import { useDispatch, useSelector } from 'react-redux'
import { Navigate, Outlet, useLocation } from 'react-router-dom'
import { SWRConfig } from 'swr'

import { api } from 'apiClient/api'
import { findCurrentRoute } from 'app/AppRouter/findCurrentRoute'
import Notification from 'components/Notification/Notification'
import { GET_DATA_ERROR_MESSAGE } from 'core/shared/constants'
import useActiveFeature from 'hooks/useActiveFeature'
import { useConfigureFirebase } from 'hooks/useAnalytics'
import useIsNewInterfaceActive from 'hooks/useIsNewInterfaceActive'
import useNotification from 'hooks/useNotification'
import { updateUser } from 'store/user/reducer'
import { selectCurrentUser } from 'store/user/selectors'

import { useOrejime } from './analytics/orejime'
import { useSentry } from './analytics/sentry'
import useFocus from './hook/useFocus'
import { useLoadFeatureFlags } from './hook/useLoadFeatureFlags'
import useLogNavigation from './hook/useLogNavigation'
import usePageTitle from './hook/usePageTitle'

window.beamer_config = { product_id: 'vjbiYuMS52566', lazy: true }

export const App = (): JSX.Element | null => {
  const isBeamerEnabled = useActiveFeature('ENABLE_BEAMER')
  const location = useLocation()
  const currentUser = useSelector(selectCurrentUser)
  const dispatch = useDispatch()
  const notify = useNotification()

  const { consentedToBeamer, consentedToFirebase } = useOrejime()
  useSentry()

  const isNewInterfaceActive = useIsNewInterfaceActive()

  useEffect(() => {
    document.documentElement.setAttribute(
      'data-theme',
      isNewInterfaceActive ? 'blue' : 'pink'
    )
  }, [isNewInterfaceActive])

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

  if (
    !currentRoute?.meta?.public &&
    !currentRoute?.path.includes('/parcours-inscription') &&
    currentUser !== null &&
    !currentUser.isAdmin &&
    !currentUser.hasUserOfferer
  ) {
    return <Navigate to="/parcours-inscription" replace />
  }

  return (
    <>
      <SWRConfig
        value={{
          onError: () => {
            notify.error(GET_DATA_ERROR_MESSAGE)
          },
          revalidateOnFocus: false,
        }}
      >
        <Outlet />
      </SWRConfig>
      <Notification />
    </>
  )
}
