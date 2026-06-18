import useSWR from 'swr'

import { api } from '@/apiClient/api'
import { GET_VENUE_PROVIDERS_QUERY_KEY } from '@/commons/config/swrQueryKeys'
import { useAppSelector } from '@/commons/hooks/useAppSelector'
import { ensureSelectedPartnerVenue } from '@/commons/store/user/selectors'

import { SynchronizationConnexions } from './components/VenueProvidersManager/SynchronizationConnexions/SynchronizationConnexions'

const SynchronizationsProviders = () => {
  const venue = useAppSelector(ensureSelectedPartnerVenue)
  const venueProvidersQuery = useSWR(
    [GET_VENUE_PROVIDERS_QUERY_KEY, venue.id],
    ([, venueIdParam]) =>
      api.listVenueProviders({ path: { venue_id: Number(venueIdParam) } })
  )
  const venueProviders = venueProvidersQuery.data?.venueProviders ?? []
  return (
    <SynchronizationConnexions venueProviders={venueProviders} venue={venue} />
  )
}

// Lazy-loaded by react-router
// ts-unused-exports:disable-next-line
export const Component = SynchronizationsProviders
