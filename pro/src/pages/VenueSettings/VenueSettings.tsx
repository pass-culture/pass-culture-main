import { useParams } from 'react-router-dom'
import useSWR from 'swr'

import { api } from 'apiClient/api'
import { OfferStatus } from 'apiClient/v1'
import { AppLayout } from 'app/AppLayout'
import {
  GET_OFFERER_QUERY_KEY,
  GET_VENUE_LABELS_QUERY_KEY,
  GET_VENUE_PROVIDERS_QUERY_KEY,
  GET_VENUE_QUERY_KEY,
  GET_VENUE_TYPES_QUERY_KEY,
} from 'config/swrQueryKeys'
import { DEFAULT_SEARCH_FILTERS } from 'core/Offers/constants'
import { useAdapter } from 'hooks'
import {
  getFilteredOffersAdapter,
  Payload,
} from 'pages/Offers/adapters/getFilteredOffersAdapter'
import Spinner from 'ui-kit/Spinner/Spinner'

import { offerHasBookingQuantity } from './offerHasBookingQuantity'
import { setInitialFormValues } from './setInitialFormValues'
import { VenueSettingsFormScreen } from './VenueSettingsScreen'

const VenueSettings = (): JSX.Element | null => {
  const { offererId, venueId } = useParams<{
    offererId: string
    venueId: string
  }>()

  const venueQuery = useSWR(
    [GET_VENUE_QUERY_KEY, venueId],
    ([, venueIdParam]) => api.getVenue(Number(venueIdParam))
  )
  const venue = venueQuery.data

  const venueLabelsQuery = useSWR(
    [GET_VENUE_LABELS_QUERY_KEY],
    () => api.fetchVenueLabels(),
    { fallbackData: [] }
  )

  const offererQuery = useSWR(
    [GET_OFFERER_QUERY_KEY, offererId],
    ([, offererIdParam]) => api.getOfferer(Number(offererIdParam))
  )
  const offerer = offererQuery.data

  const venueTypesQuery = useSWR([GET_VENUE_TYPES_QUERY_KEY], () =>
    api.getVenueTypes()
  )
  const venueTypes = venueTypesQuery.data

  const venueProvidersQuery = useSWR(
    [GET_VENUE_PROVIDERS_QUERY_KEY, Number(venueId)],
    ([, venueIdParam]) => api.listVenueProviders(venueIdParam)
  )
  const venueProviders = venueProvidersQuery.data?.venue_providers

  // TODO This is a bug!!! The /offers route is paginated so there is no guarantee that
  // hasBookingQuantity is exactly what we want
  const apiFilters = {
    ...DEFAULT_SEARCH_FILTERS,
    status: OfferStatus.ACTIVE,
    venueId: venue?.id.toString() ?? '',
  }
  const { isLoading: isLoadingVenueOffers, data: venueOffers } = useAdapter<
    Payload,
    Payload
  >(() => getFilteredOffersAdapter(apiFilters))
  const hasBookingQuantity = offerHasBookingQuantity(venueOffers?.offers)

  if (
    offererQuery.isLoading ||
    venueQuery.isLoading ||
    venueLabelsQuery.isLoading ||
    venueTypesQuery.isLoading ||
    venueProvidersQuery.isLoading ||
    !offerer ||
    !venue ||
    !venueTypes ||
    !venueProviders ||
    isLoadingVenueOffers
  ) {
    return (
      <AppLayout>
        <Spinner />
      </AppLayout>
    )
  }

  const venueLabels = venueLabelsQuery.data.map((type) => ({
    value: type.id.toString(),
    label: type.label,
  }))

  return (
    <AppLayout>
      <VenueSettingsFormScreen
        initialValues={setInitialFormValues(venue)}
        offerer={offerer}
        venueLabels={venueLabels}
        venueTypes={venueTypes}
        venue={venue}
        venueProviders={venueProviders}
        hasBookingQuantity={venue.id ? hasBookingQuantity : false}
      />
    </AppLayout>
  )
}

// Lazy-loaded by react-router-dom
// ts-unused-exports:disable-next-line
export const Component = VenueSettings
