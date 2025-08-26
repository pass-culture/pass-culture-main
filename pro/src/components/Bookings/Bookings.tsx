import { useSelector } from 'react-redux'
import { useLocation } from 'react-router'
import {
  formatAndOrderAddresses,
  formatAndOrderVenues,
} from 'repository/venuesService'
import useSWR from 'swr'

import { api } from '@/apiClient/api'
import type {
  BookingRecapResponseModel,
  CollectiveBookingResponseModel,
} from '@/apiClient/v1'
import { useAnalytics } from '@/app/App/analytics/firebase'
import {
  GET_BOOKINGS_QUERY_KEY,
  GET_HAS_BOOKINGS_QUERY_KEY,
  GET_VENUES_QUERY_KEY,
} from '@/commons/config/swrQueryKeys'
import type { PreFiltersParams } from '@/commons/core/Bookings/types'
import { Events } from '@/commons/core/FirebaseEvents/constants'
import { Audience } from '@/commons/core/shared/types'
import { useOfferer } from '@/commons/hooks/swr/useOfferer'
import { useOffererAddresses } from '@/commons/hooks/swr/useOffererAddresses'
import { useNotification } from '@/commons/hooks/useNotification'
import { selectCurrentOffererId } from '@/commons/store/offerer/selectors'
import { isEqual } from '@/commons/utils/isEqual'
import { CollectiveBudgetCallout } from '@/components/CollectiveBudgetInformation/CollectiveBudgetCallout'
import { ChoosePreFiltersMessage } from '@/pages/Bookings/ChoosePreFiltersMessage/ChoosePreFiltersMessage'

import { BookingsRecapTable } from './BookingsRecapTable/BookingsRecapTable'
import { PreFilters } from './PreFilters/PreFilters'
import { useBookingsFilters } from './useBookingsFilters'

type BookingsProps<T> = {
  locationState?: { statuses: string[] }
  audience: Audience
  getFilteredBookingsAdapter: (
    params: PreFiltersParams & { page?: number }
  ) => Promise<{ bookings: T[]; pages: number; currentPage: number }>
  getUserHasBookingsAdapter: () => Promise<boolean>
}

const MAX_LOADED_PAGES = 5

export const BookingsContainer = <
  T extends BookingRecapResponseModel | CollectiveBookingResponseModel,
>({
  locationState,
  audience,
  getFilteredBookingsAdapter,
  getUserHasBookingsAdapter,
}: BookingsProps<T>): JSX.Element => {
  const notify = useNotification()
  const { logEvent } = useAnalytics()
  const location = useLocation()

  const selectedOffererId = useSelector(selectCurrentOffererId)

  const {
    initialAppliedFilters,
    appliedPreFilters,
    selectedPreFilters,
    wereBookingsRequested,
    setWereBookingsRequested,
    urlParams,
    hasPreFilters,
    isRefreshRequired,
    updateSelectedFilters,
    applyNow,
    resetPreFilters,
    resetAndApplyPreFilters,
    updateUrl,
  } = useBookingsFilters({ audience })

  const venuesQuery = useSWR(
    [GET_VENUES_QUERY_KEY, selectedOffererId],
    ([, maybeOffererId]) => api.getVenues(undefined, false, maybeOffererId)
  )

  const venues = formatAndOrderVenues(venuesQuery.data?.venues ?? []).map(
    (venue) => ({
      id: String(venue.value),
      displayName: venue.label,
    })
  )

  const { data: offerer } = useOfferer(selectedOffererId)
  const offererAddressQuery = useOffererAddresses()
  const offererAddresses = formatAndOrderAddresses(offererAddressQuery.data)

  const { data: bookingsQuery, isLoading } = useSWR(
    !isEqual(appliedPreFilters, initialAppliedFilters)
      ? [GET_BOOKINGS_QUERY_KEY, audience, appliedPreFilters]
      : null,
    async ([, filterParams]) => {
      setWereBookingsRequested(true)
      const { bookings, pages, currentPage } = await getFilteredBookingsAdapter(
        { ...filterParams }
      )

      if (currentPage === MAX_LOADED_PAGES && currentPage < pages) {
        notify.information(
          'L’affichage des réservations a été limité à 5 000 réservations. Vous pouvez modifier les filtres pour affiner votre recherche.'
        )
      }

      return bookings
    },
    { fallbackData: [] }
  )

  // and for the presence check:
  const hasBookingsQuery = useSWR(
    [GET_HAS_BOOKINGS_QUERY_KEY, audience],
    () => getUserHasBookingsAdapter(),
    { fallbackData: true }
  )

  const resetPreFiltersWithLog = () => {
    resetPreFilters()
    logEvent(Events.CLICKED_RESET_FILTERS, { from: location.pathname })
  }

  return (
    <div className="bookings-page">
      {audience === Audience.COLLECTIVE && offerer?.allowedOnAdage && (
        <CollectiveBudgetCallout
          variant="COLLECTIVE_TABLE"
          pageName="bookings"
        />
      )}

      <PreFilters
        key={`prefilters-${audience}`} // ⬅️ remount on audience change
        selectedPreFilters={selectedPreFilters}
        updateSelectedFilters={updateSelectedFilters}
        hasPreFilters={hasPreFilters}
        isRefreshRequired={isRefreshRequired}
        applyNow={applyNow}
        resetPreFilters={resetPreFiltersWithLog}
        wereBookingsRequested={wereBookingsRequested}
        audience={audience}
        hasResult={(bookingsQuery ?? []).length > 0}
        isFiltersDisabled={!hasBookingsQuery.data}
        isLocalLoading={venuesQuery.isLoading}
        isTableLoading={isLoading}
        venues={venues}
        offererAddresses={offererAddresses}
        urlParams={urlParams}
        updateUrl={updateUrl}
      />

      {wereBookingsRequested ? (
        <BookingsRecapTable
          key={`table-${audience}`} // ⬅️ remount on audience change
          bookingsRecap={bookingsQuery}
          isLoading={isLoading}
          locationState={locationState}
          audience={audience}
          resetBookings={resetAndApplyPreFilters}
        />
      ) : hasBookingsQuery.data ? (
        <ChoosePreFiltersMessage />
      ) : null}
    </div>
  )
}
