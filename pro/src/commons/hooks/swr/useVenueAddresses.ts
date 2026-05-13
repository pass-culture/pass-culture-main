import useSWR from 'swr'

import { apiNew } from '@/apiClient/api'
import type { GetVenueAddressesWithOffersOption } from '@/apiClient/v1/new'
import { GET_VENUE_ADDRESS_QUERY_KEY } from '@/commons/config/swrQueryKeys'

import { useAppSelector } from '../useAppSelector'

export const useVenueAddresses = (
  venueOption: GetVenueAddressesWithOffersOption
) => {
  const selectedPartnerVenue = useAppSelector(
    (state) => state.user.selectedPartnerVenue
  )

  return useSWR(
    [GET_VENUE_ADDRESS_QUERY_KEY, selectedPartnerVenue?.id, venueOption],
    ([, venueIdParam]) =>
      venueIdParam
        ? apiNew.getVenueAddresses({
            path: { venue_id: venueIdParam },
            query: { withOffersOption: venueOption },
          })
        : [],
    { fallbackData: [] }
  )
}
