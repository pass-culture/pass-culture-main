import { useEffect } from 'react'
import { useDispatch, useSelector } from 'react-redux'
import {
  Navigate,
  Outlet,
  useLocation,
  useNavigate,
  useSearchParams,
} from 'react-router'
import { SWRConfig } from 'swr'

import { api } from 'apiClient/api'
import { isErrorAPIError } from 'apiClient/helpers'
import { useLogExtraProData } from 'app/App/hook/useLogExtraProData'
import { findCurrentRoute } from 'app/AppRouter/findCurrentRoute'
import {
  GET_DATA_ERROR_MESSAGE,
  SAVED_OFFERER_ID_KEY,
} from 'commons/core/shared/constants'
import { useOfferer } from 'commons/hooks/swr/useOfferer'
import { useHasAccessToDidacticOnboarding } from 'commons/hooks/useHasAccessToDidacticOnboarding'
import { useNotification } from 'commons/hooks/useNotification'
import { updateCurrentOfferer } from 'commons/store/offerer/reducer'
import {
  selectCurrentOffererId,
  selectCurrentOffererIsOnboarded,
} from 'commons/store/offerer/selectors'
import { updateUser } from 'commons/store/user/reducer'
import { selectCurrentUser } from 'commons/store/user/selectors'
import { storageAvailable } from 'commons/utils/storageAvailable'
import { Notification } from 'components/Notification/Notification'

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
  const isOffererOnboarded = useSelector(selectCurrentOffererIsOnboarded)
  const dispatch = useDispatch()
  const notify = useNotification()
  const isDidacticOnboardingEnabled = useHasAccessToDidacticOnboarding()

  // Main hooks
  useLoadFeatureFlags()
  usePageTitle()
  useFocus()

  // This is to force the offerer if the url comes from the BO
  // (without breaking everything else)
  const [searchParams] = useSearchParams()
  useEffect(() => {
    if (searchParams.get('from-bo')) {
      const structureId = Number(searchParams.get('structure'))

      api.getOfferer(structureId).then(
        (offererObj) => {
          dispatch(updateCurrentOfferer(offererObj))
        },
        () => notify.error(GET_DATA_ERROR_MESSAGE)
      )

      searchParams.delete('from-bo')
      searchParams.delete('structure')
      // eslint-disable-next-line @typescript-eslint/no-floating-promises
      navigate(
        {
          search: searchParams.toString(),
        },
        { replace: true }
      )
    }
  }, [])

  // Analytics
  const { consentedToBeamer, consentedToFirebase } = useOrejime()
  useSentry()
  useBeamer(consentedToBeamer)
  useFirebase(consentedToFirebase)
  useLogNavigation()
  useLogExtraProData()

  const selectedOffererId = useSelector(selectCurrentOffererId)

  const { error: offererApiError, isValidating: isOffererValidating } =
    useOfferer(selectedOffererId, true)

  const isAwaitingRattachment = !isOffererValidating && offererApiError

  useEffect(() => {
    if (location.search.includes('logout')) {
      api.signout()
      if (storageAvailable('localStorage')) {
        localStorage.removeItem(SAVED_OFFERER_ID_KEY)
      }
      dispatch(updateUser(null))
      dispatch(updateCurrentOfferer(null))
    }
  }, [location, dispatch])

  const currentRoute = findCurrentRoute(location)
  if (currentRoute && !currentRoute.meta?.public && currentUser === null) {
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
      isOffererOnboarded === false &&
      !isAwaitingRattachment
    ) {
      return <Navigate to="/onboarding" replace />
    }
    if (
      location.pathname.includes('onboarding') &&
      (isAwaitingRattachment ||
        (isOffererOnboarded && !searchParams.get('userHasJustOnBoarded')))
    ) {
      return <Navigate to="/accueil" replace />
    }
  }

  if (
    !currentRoute?.meta?.public &&
    !currentRoute?.path.includes('/inscription/structure') &&
    !!currentUser &&
    !currentUser.hasUserOfferer
  ) {
    return <Navigate to="/inscription/structure/recherche" replace />
  }
  return (
    <>
      <SWRConfig
        value={{
          onError: (error) => {
            if (isErrorAPIError(error) && error.status === 404) {
              // eslint-disable-next-line @typescript-eslint/no-floating-promises
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
