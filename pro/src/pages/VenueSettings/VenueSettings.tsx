import useSWR from 'swr'

import { apiNew } from '@/apiClient/api'
import { BasicLayout } from '@/app/App/layouts/BasicLayout/BasicLayout'
import { MainHeading } from '@/app/App/layouts/components/MainHeading/MainHeading'
import {
  GET_VENUE_PROVIDERS_QUERY_KEY,
  GET_VENUE_QUERY_KEY,
} from '@/commons/config/swrQueryKeys'
import { useAppSelector } from '@/commons/hooks/useAppSelector'
import { ensureSelectedPartnerVenue } from '@/commons/store/user/selectors'
import { Spinner } from '@/ui-kit/Spinner/Spinner'

import { VenueSettingsScreen } from './components/VenueSettingsScreen'

const VenueSettings = (): JSX.Element | null => {
  const venueId = useAppSelector(ensureSelectedPartnerVenue).id

  const offerer = useAppSelector(ensureSelectedPartnerVenue).managingOfferer

  const venueQuery = useSWR(
    [GET_VENUE_QUERY_KEY, venueId],
    ([, venueIdParam]) =>
      apiNew.getVenue({ path: { venue_id: Number(venueIdParam) } })
  )
  const venue = venueQuery.data

  const venueProvidersQuery = useSWR(
    [GET_VENUE_PROVIDERS_QUERY_KEY, venueId],
    ([, venueIdParam]) =>
      apiNew.listVenueProviders({ path: { venue_id: Number(venueIdParam) } })
  )
  const venueProviders = venueProvidersQuery.data?.venueProviders

  const isNotReady =
    venueQuery.isLoading ||
    venueProvidersQuery.isLoading ||
    !offerer ||
    !venue ||
    !venueProviders

  return (
    <BasicLayout>
      <MainHeading mainHeading="Paramètres généraux" />
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
