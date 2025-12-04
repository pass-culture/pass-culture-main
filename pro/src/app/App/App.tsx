import { Outlet, useLocation, useNavigate } from 'react-router'
import { SWRConfig } from 'swr'

import { isErrorAPIError } from '@/apiClient/helpers'
import { useLogExtraProData } from '@/app/App/hook/useLogExtraProData'
import { GET_DATA_ERROR_MESSAGE } from '@/commons/core/shared/constants'
import { useActiveFeature } from '@/commons/hooks/useActiveFeature'
import { useNotification } from '@/commons/hooks/useNotification'
import { Notification } from '@/components/Notification/Notification'
import { SnowFlakes } from '@/components/SnowFlakes/SnowFlakes'

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
  const location = useLocation()

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

  const showSnowFlakes = useActiveFeature('TEMP_SNOWFLAKES')

  return (
    <>
      <SWRConfig
        value={{
          onError: (error) => {
            if (isErrorAPIError(error) && error.status === 404) {
              if (location.pathname.startsWith('/adage-iframe')) {
                return
              }
              // eslint-disable-next-line @typescript-eslint/no-floating-promises
              navigate('/404')
              return
            }
            notify.error(GET_DATA_ERROR_MESSAGE)
          },
          revalidateOnFocus: false,
        }}
      >
        {showSnowFlakes && <SnowFlakes />}
        <Outlet />
      </SWRConfig>
      <Notification />
    </>
  )
}
