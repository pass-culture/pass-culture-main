import useSWR from 'swr'

import { api } from '@/apiClient/api'
import { GET_VENUE_PROVIDERS_QUERY_KEY } from '@/commons/config/swrQueryKeys'
import { useActiveStep } from '@/commons/hooks/useActiveStep'
import { useAppSelector } from '@/commons/hooks/useAppSelector'
import { ensureSelectedPartnerVenue } from '@/commons/store/user/selectors'
import { STEP_NAMES } from '@/components/SettingsTabs/constants'
import { getPanelId, getTabId } from '@/ui-kit/Tabs/Tabs'

import { SynchronizationConnexions } from './components/VenueProvidersManager/SynchronizationConnexions/SynchronizationConnexions'

const SynchronizationsProviders = () => {
  const venue = useAppSelector(ensureSelectedPartnerVenue)
  const activeStep = useActiveStep(STEP_NAMES)
  const venueProvidersQuery = useSWR(
    [GET_VENUE_PROVIDERS_QUERY_KEY, venue.id],
    ([, venueIdParam]) =>
      api.listVenueProviders({ path: { venue_id: Number(venueIdParam) } })
  )
  const venueProviders = venueProvidersQuery.data?.venueProviders ?? []
  return (
    <div
      id={getPanelId(activeStep)}
      role="tabpanel"
      aria-labelledby={getTabId(activeStep)}
    >
      <SynchronizationConnexions
        venueProviders={venueProviders}
        venue={venue}
      />
    </div>
  )
}

// Lazy-loaded by react-router
// ts-unused-exports:disable-next-line
export const Component = SynchronizationsProviders
