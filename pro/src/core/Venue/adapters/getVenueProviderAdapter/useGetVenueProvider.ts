import { useAdapter } from 'hooks'

import getVenueProvidersAdapter from './getVenueProvidersAdapter'

const useGetVenueProvider = (venueId?: number) =>
  useAdapter(() => getVenueProvidersAdapter(venueId))

export default useGetVenueProvider
