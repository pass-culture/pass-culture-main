import { useAdapter } from 'hooks'

import getVenueProvidersAdapter from './getVenueProvidersAdapter'

const useGetVenueProvider = (venueId: string) =>
  useAdapter(() => getVenueProvidersAdapter(venueId))

export default useGetVenueProvider
