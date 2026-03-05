import useSWR from 'swr'

import { api } from '@/apiClient/api'
import type { GetVenueAddressesWithOffersOption } from '@/apiClient/v1'
import { GET_VENUE_ADDRESS_QUERY_KEY } from '@/commons/config/swrQueryKeys'

import { useAppSelector } from '../useAppSelector'

export const useVenueAddresses = (
  venueOption: GetVenueAddressesWithOffersOption
) => {
  const selectedVenue = useAppSelector((state) => state.user.selectedVenue)

  return useSWR(
    [GET_VENUE_ADDRESS_QUERY_KEY, selectedVenue?.id],
    ([, venueIdParam]) =>
      venueIdParam ? api.getVenueAddresses(venueIdParam, venueOption) : [],
    { fallbackData: [] }
  )
}
