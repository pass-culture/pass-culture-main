import React, { Fragment, useEffect, useState } from 'react'
import { useLocation } from 'react-router-dom'

import {
  BookingRecapResponseModel,
  CollectiveBookingResponseModel,
} from 'apiClient/v1'
import { Audience } from 'core/shared'

import { CollectiveBookingsTable } from './BookingsTable/CollectiveBookingsTable'
import { IndividualBookingsTable } from './BookingsTable/IndividualBookingsTable'
import {
  EMPTY_FILTER_VALUE,
  ALL_BOOKING_STATUS,
  DEFAULT_OMNISEARCH_CRITERIA,
  FilterByOmniSearch,
} from './Filters'
import { bookingIdOmnisearchFilter } from './Filters/FilterByOmniSearch/constants'
import Header from './Header'
import NoFilteredBookings from './NoFilteredBookings'
import { BookingsFilters } from './types'
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
  reloadBookings: () => void
  resetBookings: () => void
}

const BookingsRecapTable = <
  T extends BookingRecapResponseModel | CollectiveBookingResponseModel,
>({
  bookingsRecap,
  isLoading,
  locationState,
  audience,
  reloadBookings,
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
    setFilters(filters => {
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
    setFilters(filters => ({
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

  const nbBookings = filteredBookings.length

  return (
    <div>
      <div className="filters-wrapper">
        <FilterByOmniSearch
          isDisabled={isLoading}
          keywords={filters.keywords}
          selectedOmniSearchCriteria={filters.selectedOmniSearchCriteria}
          updateFilters={updateFilters}
          audience={audience}
        />
      </div>

      {nbBookings > 0 ? (
        <Fragment>
          <Header
            bookingsRecapFilteredLength={filteredBookings.length}
            isLoading={isLoading}
            queryBookingId={defaultBookingId}
            resetBookings={resetBookings}
          />

          {audience === Audience.INDIVIDUAL ? (
            <IndividualBookingsTable
              bookings={filteredBookings as BookingRecapResponseModel[]}
              bookingStatuses={filters.bookingStatus}
              updateGlobalFilters={updateGlobalFilters}
            />
          ) : (
            <CollectiveBookingsTable
              bookings={filteredBookings as CollectiveBookingResponseModel[]}
              bookingStatuses={filters.bookingStatus}
              updateGlobalFilters={updateGlobalFilters}
              reloadBookings={reloadBookings}
              defaultOpenedBookingId={defaultBookingId}
            />
          )}
        </Fragment>
      ) : (
        <NoFilteredBookings resetFilters={resetAllFilters} />
      )}
    </div>
  )
}

export default BookingsRecapTable
