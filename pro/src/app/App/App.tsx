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
import {
  GET_DATA_ERROR_MESSAGE,
  SAVED_OFFERER_ID_KEY,
} from 'commons/core/shared/constants'
import { useActiveFeature } from 'commons/hooks/useActiveFeature'
import { useNotification } from 'commons/hooks/useNotification'
import { updateSelectedOffererId } from 'commons/store/offerer/reducer'
import { selecteOffererIsOnboarded } from 'commons/store/offerer/selectors'
import { updateUser } from 'commons/store/user/reducer'
import { selectCurrentUser } from 'commons/store/user/selectors'
import { localStorageAvailable } from 'commons/utils/localStorageAvailable'
import { Notification } from 'components/Notification/Notification'
import { SAVED_VENUE_ID_KEY } from 'pages/Homepage/components/Offerers/components/PartnerPages/PartnerPages'

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
  const isOffererOnboarded = useSelector(selecteOffererIsOnboarded)
  const dispatch = useDispatch()
  const notify = useNotification()
  const isDidacticOnboardingEnabled = useActiveFeature(
    'WIP_ENABLE_PRO_DIDACTIC_ONBOARDING'
  )

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

  useEffect(() => {
    if (location.search.includes('logout')) {
      api.signout()
      if (localStorageAvailable()) {
        localStorage.removeItem(SAVED_OFFERER_ID_KEY)
        localStorage.removeItem(SAVED_VENUE_ID_KEY)
      }
      dispatch(updateUser(null))
      dispatch(updateSelectedOffererId(null))
    }
  }, [location, dispatch])

  const currentRoute = findCurrentRoute(location)
  if (!currentRoute?.meta?.public && currentUser === null) {
    const fromUrl = encodeURIComponent(`${location.pathname}${location.search}`)
    const loginUrl =
      fromUrl.includes('logout') || location.pathname === '/'
        ? '/connexion'
        : `/connexion?de=${fromUrl}`

    return <Navigate to={loginUrl} replace />
  }

  if (isDidacticOnboardingEnabled) {
    if (
      location.pathname.includes('accueil') &&
      isOffererOnboarded !== null &&
      !isOffererOnboarded
    ) {
      return <Navigate to="/onboarding" replace />
    }
    if (location.pathname.includes('onboarding') && isOffererOnboarded) {
      return <Navigate to="/accueil" replace />
    }
  }

  if (
    !currentRoute?.meta?.public &&
    !currentRoute?.path.includes('/parcours-inscription') &&
    !!currentUser &&
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
