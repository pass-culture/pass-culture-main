import { useParams } from 'react-router-dom'
import useSWR from 'swr'

import { api } from 'apiClient/api'
import { AppLayout } from 'app/AppLayout'
import {
  GET_OFFERER_QUERY_KEY,
  GET_VENUE_LABELS_QUERY_KEY,
  GET_VENUE_PROVIDERS_QUERY_KEY,
  GET_VENUE_QUERY_KEY,
  GET_VENUE_TYPES_QUERY_KEY,
} from 'config/swrQueryKeys'
import { Spinner } from 'ui-kit/Spinner/Spinner'

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

  if (
    offererQuery.isLoading ||
    venueQuery.isLoading ||
    venueLabelsQuery.isLoading ||
    venueTypesQuery.isLoading ||
    venueProvidersQuery.isLoading ||
    !offerer ||
    !venue ||
    !venueTypes ||
    !venueProviders
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
      />
    </AppLayout>
  )
}

// Lazy-loaded by react-router-dom
// ts-unused-exports:disable-next-line
export const Component = VenueSettings
