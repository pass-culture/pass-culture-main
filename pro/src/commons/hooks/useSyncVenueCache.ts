import { useSWRConfig } from 'swr'

import { api } from '@/apiClient/api'
import type { GetVenueResponseModel } from '@/apiClient/v1'
import { GET_VENUE_QUERY_KEY } from '@/commons/config/swrQueryKeys'
import { useAppDispatch } from '@/commons/hooks/useAppDispatch'
import { setSelectedPartnerVenue } from '@/commons/store/user/reducer'

export const useSyncVenueCache = () => {
  const { mutate } = useSWRConfig()
  const dispatch = useAppDispatch()

  const syncVenue = async (venueId: number) => {
    await mutate(
      [GET_VENUE_QUERY_KEY, venueId],
      async () => {
        const updatedVenue = await api.getVenue(venueId)
        dispatch(setSelectedPartnerVenue(updatedVenue))
        return updatedVenue
      },
      { revalidate: true }
    )
  }

  const syncVenueWithData = async (
    venueId: number,
    venueData: GetVenueResponseModel
  ) => {
    await mutate([GET_VENUE_QUERY_KEY, venueId], venueData, {
      revalidate: false,
    })
    dispatch(setSelectedPartnerVenue(venueData))
  }

  return { syncVenue, syncVenueWithData }
}
