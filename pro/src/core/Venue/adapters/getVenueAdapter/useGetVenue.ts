import { Venue } from 'core/Venue/types'
import { useAdapter } from 'hooks'

import { getVenueAdapter } from '.'

const useGetVenue = (venueId?: number) =>
  useAdapter<Venue, null>(() => getVenueAdapter(venueId))

export default useGetVenue
