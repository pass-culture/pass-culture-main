import { useSelector } from 'react-redux'
import useSWR from 'swr'

import { api } from '@/apiClient/api'
import type { GetOffererAddressesWithOffersOption } from '@/apiClient/v1/models/GetOffererAddressesWithOffersOption'
import { GET_OFFERER_ADDRESS_QUERY_KEY } from '@/commons/config/swrQueryKeys'
import { selectCurrentOffererId } from '@/commons/store/offerer/selectors'

export const useOffererAddresses = (
  offersOption: GetOffererAddressesWithOffersOption
) => {
  const selectedOffererId = useSelector(selectCurrentOffererId)

  return useSWR(
    [GET_OFFERER_ADDRESS_QUERY_KEY, selectedOffererId],
    ([, offererIdParam]) =>
      offererIdParam
        ? api.getOffererAddresses(offererIdParam, offersOption)
        : [],
    { fallbackData: [] }
  )
}
