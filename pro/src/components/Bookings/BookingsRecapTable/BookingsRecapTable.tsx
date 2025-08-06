import { useEffect, useState } from 'react'
import { useLocation } from 'react-router'

import {
  BookingRecapResponseModel,
  CollectiveBookingResponseModel,
} from '@/apiClient/v1'
import { Audience } from '@/commons/core/shared/types'

import { isCollectiveBooking } from './BookingsTable/Cells/BookingOfferCell'
import { CollectiveBookingsTable } from './BookingsTable/CollectiveBookingsTable'
import { IndividualBookingsTable } from './BookingsTable/IndividualBookingsTable'
import {
  ALL_BOOKING_STATUS,
  bookingIdOmnisearchFilter,
  DEFAULT_OMNISEARCH_CRITERIA,
  EMPTY_FILTER_VALUE,
} from './Filters/constants'
import { FilterByOmniSearch } from './Filters/FilterByOmniSearch'
import styles from './Filters/Filters.module.scss'
import { Header } from './Header/Header'
import { BookingsFilters } from './types'
import { filterBookingsRecap } from './utils/filterBookingsRecap'

const areCollectiveBookings = (
  bookings: (BookingRecapResponseModel | CollectiveBookingResponseModel)[]
): bookings is CollectiveBookingResponseModel[] =>
  bookings.every(isCollectiveBooking)

const areIndividualBookings = (
  bookings: (BookingRecapResponseModel | CollectiveBookingResponseModel)[]
): bookings is BookingRecapResponseModel[] =>
  bookings.every((booking) => !isCollectiveBooking(booking))

interface BookingsRecapTableProps<
  T extends BookingRecapResponseModel | CollectiveBookingResponseModel,
> {
  bookingsRecap: T[]
  isLoading: boolean
  locationState?: {
    statuses: string[]
  }
  audience: Audience
  resetBookings: () => void
}

export const BookingsRecapTable = <
  T extends BookingRecapResponseModel | CollectiveBookingResponseModel,
>({
  bookingsRecap,
  isLoading,
  locationState,
  audience,
  resetBookings,
}: BookingsRecapTableProps<T>) => {
  const [filteredBookings, setFilteredBookings] = useState(bookingsRecap)
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
  }, [bookingsRecap])

  const updateGlobalFilters = (updatedFilters: Partial<BookingsFilters>) => {
    setFilters((filters) => {
      const newFilters = { ...filters, ...updatedFilters }
      applyFilters(newFilters)
      return newFilters
    })
  }

  const applyFilters = (filtersBookingResults?: BookingsFilters) => {
    const filtersToApply = filtersBookingResults || filters
    const bookingsRecapFiltered = filterBookingsRecap(
      bookingsRecap,
      filtersToApply
    )
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
      <div className={styles['filters-wrapper']}>
        <FilterByOmniSearch
          isDisabled={isLoading}
          keywords={filters.keywords}
          selectedOmniSearchCriteria={filters.selectedOmniSearchCriteria}
          updateFilters={updateFilters}
          audience={audience}
        />
      </div>
      {filteredBookings.length !== 0 && (
        <Header
          bookingsRecapFilteredLength={filteredBookings.length}
          isLoading={isLoading}
          queryBookingId={defaultBookingId}
          resetBookings={resetBookings}
        />
      )}
      {audience === Audience.INDIVIDUAL &&
        areIndividualBookings(filteredBookings) && (
          <IndividualBookingsTable
            bookings={filteredBookings}
            bookingStatuses={filters.bookingStatus}
            updateGlobalFilters={updateGlobalFilters}
            resetFilters={resetAllFilters}
          />
        )}
      {audience === Audience.COLLECTIVE &&
        areCollectiveBookings(filteredBookings) && (
          <CollectiveBookingsTable
            bookings={filteredBookings}
            bookingStatuses={filters.bookingStatus}
            updateGlobalFilters={updateGlobalFilters}
            defaultOpenedBookingId={defaultBookingId}
            resetFilters={resetAllFilters}
          />
        )}
    </div>
  )
}
