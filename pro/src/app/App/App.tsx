import { Outlet, useNavigate } from 'react-router'
import { SWRConfig } from 'swr'

import { isErrorAPIError } from '@/apiClient/helpers'
import { ApiError } from '@/apiClient/v1'
import { useLogExtraProData } from '@/app/App/hook/useLogExtraProData'
import { GET_DATA_ERROR_MESSAGE } from '@/commons/core/shared/constants'
import { useAppDispatch } from '@/commons/hooks/useAppDispatch'
import { useNotification } from '@/commons/hooks/useNotification'
import { logout } from '@/commons/store/user/dispatchers/logout'
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
  const navigate = useNavigate()
  const notify = useNotification()
  const dispatch = useAppDispatch()

  // Main hooks
  useLoadFeatureFlags()
  usePageTitle()
  useFocus()

  // Analytics
  const { consentedToBeamer, consentedToFirebase } = useOrejime()
  useSentry()
  useBeamer(consentedToBeamer)
  useFirebase(consentedToFirebase)
  useLogNavigation()
  useLogExtraProData()

  return (
    <>
      <SWRConfig
        value={{
          onError: (error) => {
            if (error instanceof ApiError && error.status === 401) {
              // A call to users/current is made on all routes
              // including public routes
              // when user is not connected we always recieve a 401 error
              // so in that case we don't redirect to the login page (since the route is public)
              // when navigating in private routes, others calls will throw a 401
              // and redirect the user to the login page except if the call is made to users/signin
              if (
                !error.url.includes('/users/current') &&
                !error.url.includes('/offerers/names') &&
                !error.url.includes('/users/signin')
              ) {
                dispatch(logout())

                return
              }
            }

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
