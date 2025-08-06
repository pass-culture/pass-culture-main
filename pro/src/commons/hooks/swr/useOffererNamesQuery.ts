import { useDispatch, useSelector } from 'react-redux'
import useSWR, { SWRResponse } from 'swr'

import { api } from '@/apiClient/api'
import { GetOfferersNamesResponseModel } from '@/apiClient/v1'
import { GET_OFFERER_NAMES_QUERY_KEY } from '@/commons/config/swrQueryKeys'
import { updateOffererNames } from '@/commons/store/offerer/reducer'
import { selectOffererNames } from '@/commons/store/offerer/selectors'

/**
 * Custom hook to fetch the list of offerer names
 *
 * This hook combines Redux store data with a SWR request to get
 * the list of offerer names. If the data is already present in the store,
 * it is returned immediately without making a new request.
 * Else, we perform the query and dispatch it to the store.
 *
 * @returns {SWRResponse<GetOfferersNamesResponseModel>} An object containing:
 * - data: The offerer names data
 * - isLoading: Loading state
 * - isValidating: Validation state
 * - error: Potential error
 */
export const useOffererNamesQuery =
  (): SWRResponse<GetOfferersNamesResponseModel> => {
    const storeOffererNames = useSelector(selectOffererNames)
    const dispatch = useDispatch()

    const offererNamesQuery = useSWR(
      [GET_OFFERER_NAMES_QUERY_KEY],
      async () => {
        if (!storeOffererNames) {
          const response = await api.listOfferersNames()
          dispatch(updateOffererNames(response.offerersNames))
          return response
        } else {
          return {
            offerersNames: storeOffererNames,
          }
        }
      },
      {
        shouldRetryOnError: false,
      }
    )

    return offererNamesQuery
  }
