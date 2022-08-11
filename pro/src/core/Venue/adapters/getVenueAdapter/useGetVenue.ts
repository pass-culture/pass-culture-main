import { IVenue } from 'core/Venue/types'
import { useAdapter } from 'hooks'

import { getVenueAdapter } from '.'

const useGetVenue = (venueId?: string) =>
  useAdapter<IVenue, null>(() => getVenueAdapter(venueId))

export default useGetVenue
