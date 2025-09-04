import { useMemo, useState } from 'react'
import { useSelector } from 'react-redux'
import { useLocation } from 'react-router'
import {
  formatAndOrderAddresses,
  formatAndOrderVenues,
} from 'repository/venuesService'
import useSWR from 'swr'

import { api } from '@/apiClient/api'
import {
  type BookingRecapResponseModel,
  GetOffererAddressesWithOffersOption,
} from '@/apiClient/v1'
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
import { isEqual } from '@/commons/utils/isEqual'
import { NoData } from '@/components/NoData/NoData'
import { ChoosePreFiltersMessage } from '@/pages/Bookings/ChoosePreFiltersMessage/ChoosePreFiltersMessage'
import { NoBookingsForPreFiltersMessage } from '@/pages/Bookings/NoBookingsForPreFiltersMessage/NoBookingsForPreFiltersMessage'
import { Spinner } from '@/ui-kit/Spinner/Spinner'

import {
  ALL_BOOKING_STATUS,
  bookingIdOmnisearchFilter,
  DEFAULT_OMNISEARCH_CRITERIA,
  EMPTY_FILTER_VALUE,
} from './BookingsRecapTable/Filters/constants'
import { FilterByOmniSearch } from './BookingsRecapTable/Filters/FilterByOmniSearch'
import { Header } from './BookingsRecapTable/Header/Header'
import { IndividualBookingsTable } from './BookingsRecapTable/IndividualBookingsTable/IndividualBookingsTable'
import type { BookingsFilters } from './BookingsRecapTable/types'
import { filterBookingsRecap } from './BookingsRecapTable/utils/filterBookingsRecap'
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

export const IndividualBookingsComponent = <
  T extends BookingRecapResponseModel,
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

  const offererAddressQuery = useOffererAddresses(
    GetOffererAddressesWithOffersOption.INDIVIDUAL_OFFERS_ONLY
  )
  const offererAddresses = formatAndOrderAddresses(offererAddressQuery.data)

  const { data: bookingsQuery, isLoading } = useSWR(
    !isEqual(appliedPreFilters, initialAppliedFilters)
      ? [GET_BOOKINGS_QUERY_KEY, appliedPreFilters]
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

  // Omni-search state
  const queryParams = new URLSearchParams(location.search)
  const [defaultBookingId, setDefaultBookingId] = useState(
    queryParams.get('bookingId') || EMPTY_FILTER_VALUE
  )

  const baseOmniFilters: BookingsFilters = {
    bookingBeneficiary: EMPTY_FILTER_VALUE,
    bookingToken: EMPTY_FILTER_VALUE,
    offerISBN: EMPTY_FILTER_VALUE,
    offerName: EMPTY_FILTER_VALUE,
    bookingInstitution: EMPTY_FILTER_VALUE,
    bookingStatus: locationState?.statuses?.length
      ? locationState.statuses
      : [...ALL_BOOKING_STATUS],
    keywords: '',
    selectedOmniSearchCriteria: DEFAULT_OMNISEARCH_CRITERIA,
    bookingId: EMPTY_FILTER_VALUE,
  }

  const [filters, setFilters] = useState<BookingsFilters>({
    ...baseOmniFilters,
    // initialize from query if present
    selectedOmniSearchCriteria: defaultBookingId
      ? bookingIdOmnisearchFilter.id
      : DEFAULT_OMNISEARCH_CRITERIA,
    keywords: defaultBookingId,
    bookingId: defaultBookingId,
  })

  // Derive filtered list
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

  const hasBookingsQuery = useSWR(
    [GET_HAS_BOOKINGS_QUERY_KEY],
    () => getUserHasBookingsAdapter(),
    { fallbackData: true }
  )

  const resetPreFiltersWithLog = () => {
    resetPreFilters()
    logEvent(Events.CLICKED_RESET_FILTERS, { from: location.pathname })
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

      <FilterByOmniSearch
        isDisabled={isLoading}
        keywords={filters.keywords}
        selectedOmniSearchCriteria={filters.selectedOmniSearchCriteria}
        updateFilters={updateFilters}
        audience={audience}
      />
      {filteredBookings.length !== 0 && (
        <Header
          bookingsRecapFilteredLength={filteredBookings.length}
          isLoading={isLoading}
          queryBookingId={defaultBookingId}
          resetBookings={resetAndApplyPreFilters}
        />
      )}

      {wereBookingsRequested ? (
        (bookingsQuery ?? []).length > 0 ? (
          <IndividualBookingsTable
            bookings={filteredBookings}
            bookingStatuses={filters.bookingStatus}
            updateGlobalFilters={updateGlobalFilters}
            resetFilters={resetAndApplyPreFilters}
          />
        ) : isLoading ? (
          <Spinner />
        ) : (
          <NoBookingsForPreFiltersMessage
            resetPreFilters={resetPreFiltersWithLog}
          />
        )
      ) : hasBookingsQuery.data ? (
        <ChoosePreFiltersMessage />
      ) : (
        <NoData page="bookings" />
      )}
    </div>
  )
}
