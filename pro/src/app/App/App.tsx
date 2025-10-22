import { useEffect } from 'react'
import { useDispatch } from 'react-redux'
import { Outlet, useNavigate, useSearchParams } from 'react-router'
import useSWR, { SWRConfig } from 'swr'

import { api } from '@/apiClient/api'
import { isErrorAPIError } from '@/apiClient/helpers'
import type { GetOffererResponseModel } from '@/apiClient/v1'
import { useLogExtraProData } from '@/app/App/hook/useLogExtraProData'
import { GET_OFFERER_QUERY_KEY } from '@/commons/config/swrQueryKeys'
import { GET_DATA_ERROR_MESSAGE } from '@/commons/core/shared/constants'
import { useNotification } from '@/commons/hooks/useNotification'
import { updateCurrentOfferer } from '@/commons/store/offerer/reducer'
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
  const dispatch = useDispatch()
  const notify = useNotification()

  // Main hooks
  useLoadFeatureFlags()
  usePageTitle()
  useFocus()

  const [searchParams] = useSearchParams()

  const fromBo = searchParams.get('from-bo')
  const offererId = fromBo ? Number(searchParams.get('structure')) : null

  const { data: offerer } = useSWR<
    GetOffererResponseModel,
    string,
    [string, number] | null
  >(
    offererId ? [GET_OFFERER_QUERY_KEY, offererId] : null,
    ([, offererIdParam]) => api.getOfferer(offererIdParam)
  )

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
