import { useParams } from 'react-router-dom'
import useSWR from 'swr'

import { api } from 'apiClient/api'
import { OfferStatus } from 'apiClient/v1'
import { AppLayout } from 'app/AppLayout'
import { DEFAULT_SEARCH_FILTERS } from 'core/Offers/constants'
import { useGetVenueTypes } from 'core/Venue/adapters/getVenueTypeAdapter'
import { useAdapter } from 'hooks'
import {
  getFilteredOffersAdapter,
  Payload,
} from 'pages/Offers/adapters/getFilteredOffersAdapter'
import Spinner from 'ui-kit/Spinner/Spinner'

import useGetProviders from '../../core/Venue/adapters/getProviderAdapter/useGetProvider'
import useGetVenueProviders from '../../core/Venue/adapters/getVenueProviderAdapter/useGetVenueProvider'

import { offerHasBookingQuantity } from './offerHasBookingQuantity'
import { setInitialFormValues } from './setInitialFormValues'
import { VenueSettingsFormScreen } from './VenueSettingsScreen'

const GET_VENUE_QUERY_KEY = 'getVenue'
const GET_VENUE_LABELS_QUERY_KEY = 'getVenueLabels'
export const GET_OFFERER_QUERY_KEY = 'getOfferer'

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

  const { isLoading: isLoadingVenueTypes, data: venueTypes } =
    useGetVenueTypes()
  const { isLoading: isLoadingProviders, data: providers } = useGetProviders(
    Number(venueId)
  )
  const { isLoading: isLoadingVenueProviders, data: venueProviders } =
    useGetVenueProviders(Number(venueId))

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
    venueQuery.isLoading ||
    venueLabelsQuery.isLoading ||
    isLoadingVenueTypes ||
    isLoadingProviders ||
    isLoadingVenueProviders ||
    offererQuery.isLoading ||
    isLoadingVenueOffers ||
    !venue ||
    !offerer ||
    !venueTypes
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
        providers={providers}
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
