import useSWR from 'swr'

import { api } from '@/apiClient/api'
import {
  GetOffererAddressesWithOffersOption,
  GetVenueAddressesWithOffersOption,
} from '@/apiClient/v1'
import { useAnalytics } from '@/app/App/analytics/firebase'
import { MainHeading } from '@/app/App/layouts/components/MainHeading/MainHeading'
import { GET_OFFERER_ADDRESS_QUERY_KEY } from '@/commons/config/swrQueryKeys'
import { Events } from '@/commons/core/FirebaseEvents/constants'
import { formatAndOrderAddresses } from '@/commons/format/venuesService'
import { useVenueAddresses } from '@/commons/hooks/swr/useVenueAddresses'
import { useAppSelector } from '@/commons/hooks/useAppSelector'
import { useCurrentRoute } from '@/commons/hooks/useCurrentRoute'
import { ensureSelectedAdminOfferer } from '@/commons/store/user/selectors'
import { PreFilters } from '@/components/Bookings/Components/PreFilters/PreFilters'
import { useBookingsFilters } from '@/components/Bookings/Components/useBookingsFilters'

import styles from './IndividualActivityData.module.scss'

const IndividualActivityData = () => {
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

  const offererAddressQuery = useSWR(
    [GET_OFFERER_ADDRESS_QUERY_KEY, selectedAdminOfferer.id],
    ([, offererIdParam]) =>
      offererIdParam
        ? api.getOffererAddresses(
            offererIdParam,
            GetOffererAddressesWithOffersOption.INDIVIDUAL_OFFERS_ONLY
          )
        : [],
    { fallbackData: [] }
  )
  const venueAddressQuery = useVenueAddresses(
    GetVenueAddressesWithOffersOption.INDIVIDUAL_OFFERS_ONLY
  )
  const offererAddresses = formatAndOrderAddresses(venueAddressQuery.data)

  const resetPreFiltersAndLog = () => {
    resetPreFilters()
    logEvent(Events.CLICKED_RESET_FILTERS, { from: currentRoute.pathname })
  }

  return (
    <>
      <MainHeading mainHeading="Données d'activité : individuel" />
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
