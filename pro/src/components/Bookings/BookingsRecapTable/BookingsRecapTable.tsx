// ./BookingsRecapTable/BookingsRecapTable.tsx

import { useEffect, useMemo, useState } from 'react'
import { useLocation } from 'react-router'

import type {
  BookingRecapResponseModel,
  CollectiveBookingResponseModel,
} from '@/apiClient/v1'
import { useAnalytics } from '@/app/App/analytics/firebase'
import type { Audience } from '@/commons/core/shared/types'
import { pluralize } from '@/commons/utils/pluralize'

import styles from './BookingRecapTable.module.scss'
import { BookingsTable } from './BookingsTable/BookingTable'
import {
  ALL_BOOKING_STATUS,
  bookingIdOmnisearchFilter,
  DEFAULT_OMNISEARCH_CRITERIA,
  EMPTY_FILTER_VALUE,
} from './Filters/constants'
import { FilterByOmniSearch } from './Filters/FilterByOmniSearch'
import type { BookingsFilters } from './types'
import { filterBookingsRecap } from './utils/filterBookingsRecap'

interface BookingsRecapTableProps<
  T extends BookingRecapResponseModel | CollectiveBookingResponseModel,
> {
  bookingsRecap: T[]
  isLoading: boolean
  locationState?: { statuses: string[] }
  audience: Audience
  resetBookings?: () => void
}

export const BookingsRecapTable = <
  T extends BookingRecapResponseModel | CollectiveBookingResponseModel,
>({
  isLoading,
  locationState,
  audience,
  resetBookings,
  bookingsRecap: bookings, // source list
}: BookingsRecapTableProps<T>) => {
  const { logEvent } = useAnalytics()
  const location = useLocation()
  const queryParams = new URLSearchParams(location.search)

  // default expanded by bookingId from URL (if any)
  const [defaultBookingId, setDefaultBookingId] = useState(
    queryParams.get('bookingId') || EMPTY_FILTER_VALUE
  )

  // table-level filters (omnisearch, status…)
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

  // derive filtered list
  const filteredBookings = useMemo(
    () => filterBookingsRecap(bookings, filters),
    [bookings, filters]
  )

  // keep filtered in sync when source list changes
  useEffect(() => {
    // nothing to do; useMemo handles it
  }, [bookings])

  const updateGlobalFilters = (updated: Partial<BookingsFilters>) => {
    setFilters((prev) => ({ ...prev, ...updated }))
  }

  const resetAllFilters = () => {
    const base: BookingsFilters = {
      bookingBeneficiary: EMPTY_FILTER_VALUE,
      bookingToken: EMPTY_FILTER_VALUE,
      offerISBN: EMPTY_FILTER_VALUE,
      offerName: EMPTY_FILTER_VALUE,
      bookingInstitution: EMPTY_FILTER_VALUE,
      bookingStatus: [...ALL_BOOKING_STATUS],
      keywords: '',
      selectedOmniSearchCriteria: DEFAULT_OMNISEARCH_CRITERIA,
      bookingId: EMPTY_FILTER_VALUE,
    }
    setDefaultBookingId('')
    setFilters(base)
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
      <div className={styles['booking-filters-wrapper']}>
        <FilterByOmniSearch
          isDisabled={isLoading}
          keywords={filters.keywords}
          selectedOmniSearchCriteria={filters.selectedOmniSearchCriteria}
          updateFilters={updateFilters}
          audience={audience}
        />
      </div>

      {filteredBookings.length !== 0 && (
        <div className={styles['bookings-header']}>
          {pluralize(filteredBookings.length, 'réservation')}
        </div>
      )}

      <BookingsTable
        key={`table-${audience}`}
        audience={audience}
        isLoading={isLoading}
        bookings={filteredBookings}
        allBookings={bookings}
        bookingStatuses={filters.bookingStatus}
        onUpdateGlobalFilters={updateGlobalFilters}
        onResetAllFilters={resetAllFilters}
        defaultBookingId={defaultBookingId || undefined}
      />
    </div>
  )
}
