import { useSWRConfig } from 'swr'

import { apiNew } from '@/apiClient/api'
import type { GetVenueResponseModel } from '@/apiClient/v1/new'
import { GET_VENUE_QUERY_KEY } from '@/commons/config/swrQueryKeys'
import { useAppDispatch } from '@/commons/hooks/useAppDispatch'
import { setSelectedPartnerVenue } from '@/commons/store/user/reducer'

// TODO (igabriele, 2026-04-27): Replace this hook with dispatchers, what we're doing here is precisely what dispatchers are for.
export const useSyncVenueCache = () => {
  const { mutate } = useSWRConfig()
  const dispatch = useAppDispatch()

  const syncVenue = async (venueId: number) => {
    await mutate(
      [GET_VENUE_QUERY_KEY, String(venueId)],
      async () => {
        const updatedVenue = await apiNew.getVenue({
          path: { venue_id: venueId },
        })
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
    await mutate([GET_VENUE_QUERY_KEY, String(venueId)], venueData, {
      revalidate: false,
    })
    dispatch(setSelectedPartnerVenue(venueData))
  }

  return { syncVenue, syncVenueWithData }
}
