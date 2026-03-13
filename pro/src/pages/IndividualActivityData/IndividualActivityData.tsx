import {
  GetOffererAddressesWithOffersOption,
  GetVenueAddressesWithOffersOption,
} from '@/apiClient/v1'
import { useAnalytics } from '@/app/App/analytics/firebase'
import { Events } from '@/commons/core/FirebaseEvents/constants'
import { useOffererAddresses } from '@/commons/hooks/swr/useOffererAddresses'
import { useVenueAddresses } from '@/commons/hooks/swr/useVenueAddresses'
import { useActiveFeature } from '@/commons/hooks/useActiveFeature'
import { useAppSelector } from '@/commons/hooks/useAppSelector'
import { useCurrentRoute } from '@/commons/hooks/useCurrentRoute'
import { ensureSelectedAdminOfferer } from '@/commons/store/user/selectors'
import { PreFilters } from '@/components/Bookings/Components/PreFilters/PreFilters'
import { useBookingsFilters } from '@/components/Bookings/Components/useBookingsFilters'
import { formatAndOrderAddresses } from '@/repository/venuesService'

import styles from './IndividualActivityData.module.scss'

const IndividualActivityData = () => {
  const withSwitchVenueFeature = useActiveFeature('WIP_SWITCH_VENUE')
  const { logEvent } = useAnalytics()
  const selectedAdminOfferer = useAppSelector(ensureSelectedAdminOfferer)
  const currentRoute = useCurrentRoute()

  const {
    applyNow,
    hasPreFilters,
    isRefreshRequired,
    resetPreFilters,
    selectedPreFilters,
    updateSelectedFilters,
    updateUrl,
    urlParams,
    wereBookingsRequested,
  } = useBookingsFilters({
    offererId: selectedAdminOfferer.id.toString(),
  })

  const offererAddressQuery = useOffererAddresses(
    GetOffererAddressesWithOffersOption.INDIVIDUAL_OFFERS_ONLY
  )
  const venueAddressQuery = useVenueAddresses(
    GetVenueAddressesWithOffersOption.INDIVIDUAL_OFFERS_ONLY
  )
  const offererAddresses = formatAndOrderAddresses(
    withSwitchVenueFeature ? venueAddressQuery.data : offererAddressQuery.data
  )

  const resetPreFiltersAndLog = () => {
    resetPreFilters()
    logEvent(Events.CLICKED_RESET_FILTERS, { from: currentRoute.pathname })
  }

  return (
    <>
      <h2 className={styles['subtitle']}>
        Téléchargement des réservations individuelles
      </h2>

      <PreFilters
        applyNow={applyNow}
        hasPreFilters={hasPreFilters}
        hasResult={false}
        isAdministrationSpace
        isLocalLoading={offererAddressQuery.isLoading}
        isRefreshRequired={isRefreshRequired}
        isTableLoading={false}
        offererAddresses={offererAddresses}
        resetPreFilters={resetPreFiltersAndLog}
        selectedPreFilters={selectedPreFilters}
        updateSelectedFilters={updateSelectedFilters}
        updateUrl={updateUrl}
        urlParams={urlParams}
        wereBookingsRequested={wereBookingsRequested}
      />
    </>
  )
}

// Below exports are used by react-router
// ts-unused-exports:disable-next-line
export const Component = IndividualActivityData
