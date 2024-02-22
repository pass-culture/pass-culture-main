import { GetVenueResponseModel } from 'apiClient/v1'
import { useAdapter } from 'hooks'

import { getVenueAdapter } from '.'

const useGetVenue = (venueId?: number) =>
  useAdapter<GetVenueResponseModel, null>(() => getVenueAdapter(venueId))

export default useGetVenue
