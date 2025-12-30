import { useParams } from 'react-router'
import useSWR from 'swr'

import { api } from '@/apiClient/api'
import { BasicLayout } from '@/app/App/layouts/BasicLayout/BasicLayout'
import {
  GET_VENUE_PROVIDERS_QUERY_KEY,
  GET_VENUE_QUERY_KEY,
} from '@/commons/config/swrQueryKeys'
import { useAppSelector } from '@/commons/hooks/useAppSelector'
import { selectCurrentOfferer } from '@/commons/store/offerer/selectors'
import { Spinner } from '@/ui-kit/Spinner/Spinner'

import { VenueSettingsScreen } from './components/VenueSettingsScreen'

const VenueSettings = (): JSX.Element | null => {
  const { venueId } = useParams<{
    venueId: string
  }>()

  const offerer = useAppSelector(selectCurrentOfferer)

  const venueQuery = useSWR(
    [GET_VENUE_QUERY_KEY, venueId],
    ([, venueIdParam]) => api.getVenue(Number(venueIdParam))
  )
  const venue = venueQuery.data

  const venueProvidersQuery = useSWR(
    [GET_VENUE_PROVIDERS_QUERY_KEY, Number(venueId)],
    ([, venueIdParam]) => api.listVenueProviders(venueIdParam)
  )
  const venueProviders = venueProvidersQuery.data?.venueProviders

  const isNotReady =
    venueQuery.isLoading ||
    venueProvidersQuery.isLoading ||
    !offerer ||
    !venue ||
    !venueProviders

  return (
    <BasicLayout mainHeading="Paramètres généraux">
      {isNotReady ? (
        <Spinner />
      ) : (
        <VenueSettingsScreen
          offerer={offerer}
          venue={venue}
          venueProviders={venueProviders}
        />
      )}
    </BasicLayout>
  )
}

// Lazy-loaded by react-router
// ts-unused-exports:disable-next-line
export const Component = VenueSettings
