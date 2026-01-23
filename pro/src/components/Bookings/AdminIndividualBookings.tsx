import { useMemo, useState } from 'react'
import { useLocation } from 'react-router'
import useSWR from 'swr'

import { api } from '@/apiClient/api'
import type { BookingRecapResponseModel } from '@/apiClient/v1'
import { useAnalytics } from '@/app/App/analytics/firebase'
import {
  GET_BOOKINGS_QUERY_KEY,
  GET_HAS_BOOKINGS_QUERY_KEY,
} from '@/commons/config/swrQueryKeys'
import type { PreFiltersParams } from '@/commons/core/Bookings/types'
import { Events } from '@/commons/core/FirebaseEvents/constants'
import { useSnackBar } from '@/commons/hooks/useSnackBar'
import { type RootState, rootStore } from '@/commons/store/store'
import { isEqual } from '@/commons/utils/isEqual'
import { ChoosePreFiltersMessage } from '@/components/Bookings/Components/ChoosePreFiltersMessage/ChoosePreFiltersMessage'
import {
  ALL_BOOKING_STATUS,
  bookingIdOmnisearchFilter,
  DEFAULT_OMNISEARCH_CRITERIA,
  EMPTY_FILTER_VALUE,
} from '@/components/Bookings/Components/Filters/constants'
import { FilterByOmniSearch } from '@/components/Bookings/Components/Filters/FilterByOmniSearch'
import { Header } from '@/components/Bookings/Components/Header/Header'
import { AdminPreFilters } from '@/components/Bookings/Components/PreFilters/AdminPreFilters'
import type { BookingsFilters } from '@/components/Bookings/Components/types'
import { useBookingsFilters } from '@/components/Bookings/Components/useBookingsFilters'
import { filterBookingsRecap } from '@/components/Bookings/Components/utils/filterBookingsRecap'
import { IndividualBookingsTable } from '@/components/Bookings/IndividualBookingsTable/IndividualBookingsTable'
import { Spinner } from '@/ui-kit/Spinner/Spinner'

type AdminBookingsProps<T> = {
  locationState?: { statuses: string[] }
  getFilteredBookingsAdapter: (
    params: PreFiltersParams & { page?: number },
    getState: () => RootState
  ) => Promise<{ bookings: T[]; pages: number; currentPage: number }>
}

const MAX_LOADED_PAGES = 5

export function AdminIndividualBookingsComponent<
  T extends BookingRecapResponseModel,
>({
  locationState,
  getFilteredBookingsAdapter,
}: AdminBookingsProps<T>): JSX.Element {
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
  } = useBookingsFilters({
    basePath: '/admin/individuel',
  })

  const { data: bookingsQuery, isLoading } = useSWR(
    !isEqual(appliedPreFilters, initialAppliedFilters)
      ? [GET_BOOKINGS_QUERY_KEY, appliedPreFilters]
      : null,
    async ([, filterParams]) => {
      setWereBookingsRequested(true)
      const { bookings, pages, currentPage } = await getFilteredBookingsAdapter(
        { ...filterParams },
        rootStore.getState
      )

      if (currentPage === MAX_LOADED_PAGES && currentPage < pages) {
        snackBar.success(
          "L'affichage des réservations a été limité à 5 000 réservations. Vous pouvez modifier les filtres pour affiner votre recherche."
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
      <AdminPreFilters
        selectedPreFilters={selectedPreFilters}
        updateSelectedFilters={updateSelectedFilters}
        hasPreFilters={hasPreFilters}
        isRefreshRequired={isRefreshRequired}
        applyNow={applyNow}
        resetPreFilters={resetPreFiltersWithLog}
        wereBookingsRequested={wereBookingsRequested}
        hasResult={(bookingsQuery ?? []).length > 0}
        isFiltersDisabled={!hasBookingsQuery.hasBookings}
        isLocalLoading={false}
        isTableLoading={isLoading}
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
