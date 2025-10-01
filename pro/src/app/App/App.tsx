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

import { isErrorAPIError } from '@/apiClient/helpers'
import { useLogExtraProData } from '@/app/App/hook/useLogExtraProData'
import { findCurrentRoute } from '@/app/AppRouter/findCurrentRoute'
import { GET_DATA_ERROR_MESSAGE } from '@/commons/core/shared/constants'
import { useOfferer } from '@/commons/hooks/swr/useOfferer'
import { useNotification } from '@/commons/hooks/useNotification'
import { updateCurrentOfferer } from '@/commons/store/offerer/reducer'
import { selectCurrentOffererId } from '@/commons/store/offerer/selectors'
import { selectCurrentUser } from '@/commons/store/user/selectors'
import { Notification } from '@/components/Notification/Notification'

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

  const [searchParams] = useSearchParams()

  const fromBo = searchParams.get('from-bo')
  const selectedOffererId = useSelector(selectCurrentOffererId)
  const offererId = fromBo
    ? Number(searchParams.get('structure'))
    : selectedOffererId

  const { data: offerer } = useOfferer(offererId)

  useEffect(() => {
    if (searchParams.get('from-bo') && offerer) {
      dispatch(updateCurrentOfferer(offerer))

      // remove query params safely
      const next = new URLSearchParams(searchParams)
      next.delete('from-bo')
      next.delete('structure')
      navigate({ search: next.toString() }, { replace: true })
    }
  }, [offerer, dispatch, navigate, searchParams])

  // Analytics
  const { consentedToBeamer, consentedToFirebase } = useOrejime()
  useSentry()
  useBeamer(consentedToBeamer)
  useFirebase(consentedToFirebase)
  useLogNavigation()
  useLogExtraProData()

  const currentRoute = findCurrentRoute(location)

  if (currentRoute && !currentRoute.meta?.public && currentUser === null) {
    const fromUrl = encodeURIComponent(`${location.pathname}${location.search}`)

    const loginUrl =
      location.pathname === '/' ? '/connexion' : `/connexion?de=${fromUrl}`

    return <Navigate to={loginUrl} replace />
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
