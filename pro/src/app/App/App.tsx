import { useEffect } from 'react'
import { useDispatch, useSelector } from 'react-redux'
import {
  Navigate,
  Outlet,
  useLocation,
  useNavigate,
  useSearchParams,
} from 'react-router-dom'
import { SWRConfig } from 'swr'

import { api } from 'apiClient/api'
import { isErrorAPIError } from 'apiClient/helpers'
import { useLogExtraProData } from 'app/App/hook/useLogExtraProData'
import { findCurrentRoute } from 'app/AppRouter/findCurrentRoute'
import { Notification } from 'components/Notification/Notification'
import {
  GET_DATA_ERROR_MESSAGE,
  SAVED_OFFERER_ID_KEY,
} from 'core/shared/constants'
import { useIsNewInterfaceActive } from 'hooks/useIsNewInterfaceActive'
import { useNotification } from 'hooks/useNotification'
import { SAVED_VENUE_ID_KEY } from 'pages/Home/Offerers/PartnerPages'
import { updateSelectedOffererId, updateUser } from 'store/user/reducer'
import { selectCurrentUser } from 'store/user/selectors'

import { useBeamer } from './analytics/beamer'
import { useFirebase } from './analytics/firebase'
import { useOrejime } from './analytics/orejime'
import { useSentry } from './analytics/sentry'
import { useFocus } from './hook/useFocus'
import { useLoadFeatureFlags } from './hook/useLoadFeatureFlags'
import { useLogNavigation } from './hook/useLogNavigation'
import { usePageTitle } from './hook/usePageTitle'

window.beamer_config = { product_id: 'vjbiYuMS52566', lazy: true }

export const App = (): JSX.Element | null => {
  const location = useLocation()
  const navigate = useNavigate()
  const currentUser = useSelector(selectCurrentUser)
  const dispatch = useDispatch()
  const notify = useNotification()

  // Main hooks
  useLoadFeatureFlags()
  usePageTitle()
  useFocus()

  // This is to force the offerer if the url comes from the BO
  // (without breaking everything else)
  const [searchParams] = useSearchParams()
  if (searchParams.get('from-bo')) {
    dispatch(updateSelectedOffererId(Number(searchParams.get('structure'))))
  }
  // Analytics
  const { consentedToBeamer, consentedToFirebase } = useOrejime()
  useSentry()
  useBeamer(consentedToBeamer)
  useFirebase(consentedToFirebase)
  useLogNavigation()
  useLogExtraProData()

  const isNewInterfaceActive = useIsNewInterfaceActive()

  useEffect(() => {
    document.documentElement.setAttribute(
      'data-theme',
      isNewInterfaceActive ? 'blue' : 'pink'
    )
  }, [isNewInterfaceActive])

  useEffect(() => {
    if (location.search.includes('logout')) {
      // eslint-disable-next-line @typescript-eslint/no-floating-promises
      api.signout()
      localStorage.removeItem(SAVED_OFFERER_ID_KEY)
      localStorage.removeItem(SAVED_VENUE_ID_KEY)
      dispatch(updateUser(null))
      dispatch(updateSelectedOffererId(null))
    }
  }, [location])

  const currentRoute = findCurrentRoute(location)
  if (!currentRoute?.meta?.public && currentUser === null) {
    const fromUrl = encodeURIComponent(`${location.pathname}${location.search}`)
    const loginUrl =
      fromUrl.includes('logout') || location.pathname === '/'
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
          onError: (error) => {
            if (isErrorAPIError(error) && error.status === 404) {
              navigate('/404')
              return
            }
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
