import { useAdapter } from 'hooks'

import { IVenueProviderApi } from '../../types'

import getVenueProvidersAdapter from './getVenueProvidersAdapter'

const useGetVenueProvider = (venueId: string) =>
  useAdapter<IVenueProviderApi[], IVenueProviderApi[]>(() =>
    getVenueProvidersAdapter(venueId)
  )

export default useGetVenueProvider
