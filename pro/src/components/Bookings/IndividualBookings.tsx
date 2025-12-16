import { useMemo, useState } from 'react'
import { useLocation } from 'react-router'
import { formatAndOrderAddresses } from 'repository/venuesService'
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
} from '@/commons/config/swrQueryKeys'
import type { PreFiltersParams } from '@/commons/core/Bookings/types'
import { Events } from '@/commons/core/FirebaseEvents/constants'
import { useOffererAddresses } from '@/commons/hooks/swr/useOffererAddresses'
import { useSnackBar } from '@/commons/hooks/useSnackBar'
import { isEqual } from '@/commons/utils/isEqual'
import { ChoosePreFiltersMessage } from '@/components/Bookings/Components/ChoosePreFiltersMessage/ChoosePreFiltersMessage'
import { Spinner } from '@/ui-kit/Spinner/Spinner'

import {
  ALL_BOOKING_STATUS,
  bookingIdOmnisearchFilter,
  DEFAULT_OMNISEARCH_CRITERIA,
  EMPTY_FILTER_VALUE,
} from './Components/Filters/constants'
import { FilterByOmniSearch } from './Components/Filters/FilterByOmniSearch'
import { Header } from './Components/Header/Header'
import { PreFilters } from './Components/PreFilters/PreFilters'
import type { BookingsFilters } from './Components/types'
import { useBookingsFilters } from './Components/useBookingsFilters'
import { filterBookingsRecap } from './Components/utils/filterBookingsRecap'
import { IndividualBookingsTable } from './IndividualBookingsTable/IndividualBookingsTable'

type BookingsProps<T> = {
  locationState?: { statuses: string[] }
  getFilteredBookingsAdapter: (
    params: PreFiltersParams & { page?: number }
  ) => Promise<{ bookings: T[]; pages: number; currentPage: number }>
}

const MAX_LOADED_PAGES = 5

export const IndividualBookingsComponent = <
  T extends BookingRecapResponseModel,
>({
  locationState,
  getFilteredBookingsAdapter,
}: BookingsProps<T>): JSX.Element => {
  const snackBar = useSnackBar()
  const { logEvent } = useAnalytics()
  const location = useLocation()

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
  } = useBookingsFilters()

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
        snackBar.success(
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
      ? bookingIdOmnisearchFilter.value
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
    if (selectedOmniSearchCriteria === bookingIdOmnisearchFilter.value) {
      setDefaultBookingId('')
    }
    setFilters((prev) => ({
      ...prev,
      ...updatedFilter,
      keywords,
      selectedOmniSearchCriteria,
    }))
  }

  const { data: hasBookingsQuery, isLoading: hasBookingsQueryLoading } = useSWR(
    [GET_HAS_BOOKINGS_QUERY_KEY],
    () => api.getUserHasBookings()
  )

  const resetPreFiltersWithLog = () => {
    resetPreFilters()
    logEvent(Events.CLICKED_RESET_FILTERS, { from: location.pathname })
  }

  if (hasBookingsQueryLoading || !hasBookingsQuery) {
    return <Spinner />
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
        hasResult={(bookingsQuery ?? []).length > 0}
        isFiltersDisabled={!hasBookingsQuery.hasBookings}
        isLocalLoading={offererAddressQuery.isLoading}
        isTableLoading={isLoading}
        offererAddresses={offererAddresses}
        urlParams={urlParams}
        updateUrl={updateUrl}
      />

      <FilterByOmniSearch
        isDisabled={isLoading}
        keywords={filters.keywords}
        selectedOmniSearchCriteria={filters.selectedOmniSearchCriteria}
        updateFilters={updateFilters}
      />
      {filteredBookings.length !== 0 && (
        <Header
          bookingsRecapFilteredLength={filteredBookings.length}
          isLoading={isLoading}
          queryBookingId={defaultBookingId}
          resetBookings={resetAndApplyPreFilters}
        />
      )}

      {hasBookingsQuery.hasBookings && !wereBookingsRequested ? (
        <ChoosePreFiltersMessage />
      ) : (
        <IndividualBookingsTable
          bookings={filteredBookings}
          bookingStatuses={filters.bookingStatus}
          updateGlobalFilters={updateGlobalFilters}
          resetFilters={resetAndApplyPreFilters}
          isLoading={isLoading}
          hasNoBooking={!hasBookingsQuery.hasBookings}
        />
      )}
    </div>
  )
}
