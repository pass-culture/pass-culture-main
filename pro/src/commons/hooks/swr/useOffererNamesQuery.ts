import useSWR, { type SWRResponse } from 'swr'

import { api } from '@/apiClient/api'
import type { GetOffererNameResponseModel } from '@/apiClient/v1'
import { GET_OFFERER_NAMES_QUERY_KEY } from '@/commons/config/swrQueryKeys'
import { updateOffererNames } from '@/commons/store/user/reducer'

import { useAppDispatch } from '../useAppDispatch'
import { useAppSelector } from '../useAppSelector'

/**
 * Custom hook to fetch the list of offerer names
 *
 * This hook combines Redux store data with a SWR request to get
 * the list of offerer names. If the data is already present in the store,
 * it is returned immediately without making a new request.
 * Else, we perform the query and dispatch it to the store.
 *
 * @returns {SWRResponse<UseOffererNamesQueryResponse>} An object containing:
 * - data: The offerer names data
 * - isLoading: Loading state
 * - isValidating: Validation state
 * - error: Potential error
 */
export const useOffererNamesQuery = (): SWRResponse<
  GetOffererNameResponseModel[]
> => {
  const storeOffererNames = useAppSelector((state) => state.user.offererNames)
  const dispatch = useAppDispatch()

  const offererNamesQuery = useSWR<GetOffererNameResponseModel[]>(
    [GET_OFFERER_NAMES_QUERY_KEY],
    async (): Promise<GetOffererNameResponseModel[]> => {
      if (storeOffererNames) {
        return storeOffererNames
      } else {
        const response = await api.listOfferersNames()
        dispatch(updateOffererNames(response.offerersNames))
        return response.offerersNames
      }
    },
    {
      shouldRetryOnError: false,
    }
  )

  return {
    ...offererNamesQuery,
  }
}
