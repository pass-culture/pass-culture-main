import { useMemo, useState } from 'react'
import { useSelector } from 'react-redux'
import { useLocation } from 'react-router'
import {
  formatAndOrderAddresses,
  formatAndOrderVenues,
} from 'repository/venuesService'
import useSWR from 'swr'

import { api } from '@/apiClient/api'
import type { BookingRecapResponseModel } from '@/apiClient/v1'
import { useAnalytics } from '@/app/App/analytics/firebase'
import {
  GET_BOOKINGS_QUERY_KEY,
  GET_HAS_BOOKINGS_QUERY_KEY,
  GET_VENUES_QUERY_KEY,
} from '@/commons/config/swrQueryKeys'
import type { PreFiltersParams } from '@/commons/core/Bookings/types'
import { Events } from '@/commons/core/FirebaseEvents/constants'
import type { Audience } from '@/commons/core/shared/types'
import { useOffererAddresses } from '@/commons/hooks/swr/useOffererAddresses'
import { useNotification } from '@/commons/hooks/useNotification'
import { selectCurrentOffererId } from '@/commons/store/offerer/selectors'

import {
  ALL_BOOKING_STATUS,
  bookingIdOmnisearchFilter,
  DEFAULT_OMNISEARCH_CRITERIA,
  EMPTY_FILTER_VALUE,
} from './BookingsFilters/Filters/constants'
import { FilterByOmniSearch } from './BookingsFilters/Filters/FilterByOmniSearch'
import { PreFilters } from './BookingsFilters/PreFilters/PreFilters'
import type { BookingsFilters } from './BookingsFilters/types'
import { useBookingsFilters } from './BookingsFilters/useBookingsFilters'
import { filterBookingsRecap } from './BookingsFilters/utils/filterBookingsRecap'
import { Header } from './Header/Header'
import { IndividualBookingsTable } from './IndividualBookingTable/IndividualBookingsTable'

type BookingsProps<T> = {
  locationState?: { statuses: string[] }
  audience: Audience
  getFilteredBookingsAdapter: (
    params: PreFiltersParams & { page?: number }
  ) => Promise<{ bookings: T[]; pages: number; currentPage: number }>
  getUserHasBookingsAdapter: () => Promise<boolean>
}

const MAX_LOADED_PAGES = 5

export const IndividualBookings = <T extends BookingRecapResponseModel>({
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
    // wereBookingsRequested,
    // setWereBookingsRequested,
    urlParams,
    hasPreFilters,
    isRefreshRequired,
    updateSelectedFilters,
    applyNow,
    resetPreFilters,
    resetAndApplyPreFilters,
    updateUrl,
  } = useBookingsFilters({ audience })

  // Venues
  const venuesQuery = useSWR(
    [GET_VENUES_QUERY_KEY, selectedOffererId],
    ([, maybeOffererId]) => api.getVenues(undefined, false, maybeOffererId)
  )
  const venues = formatAndOrderVenues(venuesQuery.data?.venues ?? []).map(
    (v) => ({
      id: String(v.value),
      displayName: v.label,
    })
  )

  // Addresses
  const offererAddressQuery = useOffererAddresses()
  const offererAddresses = formatAndOrderAddresses(offererAddressQuery.data)

  const { data: hasBookingsQuery } = useSWR(
    [GET_HAS_BOOKINGS_QUERY_KEY, audience],
    () => getUserHasBookingsAdapter(),
    { fallbackData: false }
  )

  // Bookings
  const { data: bookingsQuery = [], isLoading } = useSWR(
    [GET_BOOKINGS_QUERY_KEY, audience, appliedPreFilters],
    async ([, , filterParams]) => {
      // setWereBookingsRequested(true)
      const { bookings, pages, currentPage } = await getFilteredBookingsAdapter(
        {
          ...filterParams,
        }
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

  const resetPreFiltersWithLog = () => {
    resetPreFilters()

    logEvent(Events.CLICKED_RESET_FILTERS, { from: location.pathname })
  }

  const queryParams = new URLSearchParams(location.search)
  const [defaultBookingId, setDefaultBookingId] = useState(
    queryParams.get('bookingId') || EMPTY_FILTER_VALUE
  )

  const [filters, setFilters] = useState<BookingsFilters>({
    bookingBeneficiary: EMPTY_FILTER_VALUE,
    bookingToken: EMPTY_FILTER_VALUE,
    offerISBN: EMPTY_FILTER_VALUE,
    offerName: EMPTY_FILTER_VALUE,
    bookingStatus: locationState?.statuses?.length
      ? locationState.statuses
      : [...ALL_BOOKING_STATUS],
    selectedOmniSearchCriteria: defaultBookingId
      ? bookingIdOmnisearchFilter.id
      : DEFAULT_OMNISEARCH_CRITERIA,
    keywords: defaultBookingId,
    bookingInstitution: EMPTY_FILTER_VALUE,
    bookingId: defaultBookingId,
  })

  const filteredBookings = useMemo(
    () => filterBookingsRecap(bookingsQuery, filters),
    [bookingsQuery, filters]
  )

  const updateGlobalFilters = (updatedFilters: Partial<BookingsFilters>) => {
    setFilters((prev) => ({ ...prev, ...updatedFilters }))
  }

  const updateFilters = (
    updatedFilter: Partial<BookingsFilters>,
    updatedSelectedContent: {
      keywords: string
      selectedOmniSearchCriteria: string
    }
  ) => {
    const { keywords, selectedOmniSearchCriteria } = updatedSelectedContent
    if (selectedOmniSearchCriteria === bookingIdOmnisearchFilter.id) {
      setDefaultBookingId('')
    }
    setFilters((prev) => ({
      ...prev,
      ...updatedFilter,
      keywords,
      selectedOmniSearchCriteria,
    }))
  }

  return (
    <div>
      <PreFilters
        selectedPreFilters={selectedPreFilters}
        updateSelectedFilters={updateSelectedFilters}
        hasPreFilters={hasPreFilters}
        isRefreshRequired={isRefreshRequired}
        applyNow={applyNow}
        resetPreFilters={resetPreFiltersWithLog}
        audience={audience}
        hasResult={bookingsQuery.length > 0}
        isFiltersDisabled={!hasBookingsQuery}
        isLocalLoading={venuesQuery.isLoading}
        isTableLoading={isLoading}
        venues={venues}
        offererAddresses={offererAddresses}
        urlParams={urlParams}
        updateUrl={updateUrl}
      />
      <div>
        {bookingsQuery.length > 0 && (
          <FilterByOmniSearch
            isDisabled={isLoading}
            keywords={filters.keywords}
            selectedOmniSearchCriteria={filters.selectedOmniSearchCriteria}
            updateFilters={updateFilters}
            audience={audience}
          />
        )}
        {filteredBookings.length !== 0 && (
          <Header
            bookingsRecapFilteredLength={filteredBookings.length}
            isLoading={isLoading}
            queryBookingId={defaultBookingId}
            resetBookings={resetAndApplyPreFilters}
          />
        )}

        <IndividualBookingsTable
          bookings={filteredBookings}
          bookingStatuses={filters.bookingStatus}
          updateGlobalFilters={updateGlobalFilters}
          resetFilters={resetAndApplyPreFilters}
          isLoading={isLoading}
          hasBookings={filteredBookings.length > 0}
        />
      </div>
    </div>
  )
}
