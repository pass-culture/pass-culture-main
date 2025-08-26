import { useEffect, useState } from 'react'
import { useLocation } from 'react-router'

import type {
  BookingRecapResponseModel,
  CollectiveBookingResponseModel,
} from '@/apiClient/v1'
import { Audience } from '@/commons/core/shared/types'

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
  locationState?: {
    statuses: string[]
  }
  audience: Audience
  resetBookings?: () => void
}

export const BookingsRecapTable = <
  T extends BookingRecapResponseModel | CollectiveBookingResponseModel,
>({
  isLoading,
  locationState,
  audience,
  bookingsRecap: bookings,
}: BookingsRecapTableProps<T>) => {
  const [filteredBookings, setFilteredBookings] = useState(bookings)

  const location = useLocation()
  const queryParams = new URLSearchParams(location.search)
  const [defaultBookingId, setDefaultBookingId] = useState(
    queryParams.get('bookingId') || EMPTY_FILTER_VALUE
  )

  const [filters, setFilters] = useState<BookingsFilters>({
    bookingBeneficiary: EMPTY_FILTER_VALUE,
    bookingToken: EMPTY_FILTER_VALUE,
    offerISBN: EMPTY_FILTER_VALUE,
    offerName: EMPTY_FILTER_VALUE,
    bookingStatus: locationState?.statuses.length
      ? locationState.statuses
      : [...ALL_BOOKING_STATUS],
    selectedOmniSearchCriteria: defaultBookingId
      ? bookingIdOmnisearchFilter.id
      : DEFAULT_OMNISEARCH_CRITERIA,
    keywords: defaultBookingId,
    bookingInstitution: EMPTY_FILTER_VALUE,
    bookingId: defaultBookingId,
  })

  useEffect(() => {
    applyFilters()
  }, [bookings])

  const updateGlobalFilters = (updatedFilters: Partial<BookingsFilters>) => {
    setFilters((filters) => {
      const newFilters = { ...filters, ...updatedFilters }
      applyFilters(newFilters)
      return newFilters
    })
  }

  const applyFilters = (filtersBookingResults?: BookingsFilters) => {
    const filtersToApply = filtersBookingResults || filters
    const bookingsRecapFiltered = filterBookingsRecap(bookings, filtersToApply)
    setFilteredBookings(bookingsRecapFiltered)
  }

  const resetAllFilters = () => {
    const filtersBookingResults = {
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
    setFilters(filtersBookingResults)
    applyFilters(filtersBookingResults)
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
    setFilters((filters) => ({
      ...filters,
      ...updatedFilter,
      keywords,
      selectedOmniSearchCriteria,
    }))
    applyFilters({
      ...filters,
      ...updatedFilter,
    })
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
