import { Outlet, useLocation, useNavigate } from 'react-router'
import { SWRConfig } from 'swr'

import { isErrorAPIError } from '@/apiClient/helpers'
import { useLogExtraProData } from '@/app/App/hook/useLogExtraProData'
import { GET_DATA_ERROR_MESSAGE } from '@/commons/core/shared/constants'
import { useSnackBar } from '@/commons/hooks/useSnackBar'
import { SnackBarContainer } from '@/components/SnackBarContainer/SnackBarContainer'

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
  const snackBar = useSnackBar()
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
            snackBar.error(GET_DATA_ERROR_MESSAGE)
          },
          revalidateOnFocus: false,
        }}
      >
        <Outlet />
      </SWRConfig>
      <SnackBarContainer />
    </>
  )
}
