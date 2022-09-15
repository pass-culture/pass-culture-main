import React, { Fragment, useEffect, useMemo, useState } from 'react'
import type { Column } from 'react-table'

import {
  BookingRecapResponseModel,
  CollectiveBookingResponseModel,
} from 'apiClient/v1'
import { Audience } from 'core/shared'

import {
  FilterByOmniSearch,
  Header,
  NoFilteredBookings,
  ALL_BOOKING_STATUS,
  DEFAULT_OMNISEARCH_CRITERIA,
  EMPTY_FILTER_VALUE,
  TableWrapper,
} from './components'
import { NB_BOOKINGS_PER_PAGE } from './constants'
import { BookingsFilters } from './types'
import { filterBookingsRecap, getColumnsByAudience } from './utils'

const FIRST_PAGE_INDEX = 0

interface IBookingsRecapTableProps<
  T extends BookingRecapResponseModel | CollectiveBookingResponseModel
> {
  bookingsRecap: T[]
  isLoading: boolean
  locationState?: {
    statuses: string[]
  }
  audience: Audience
}

const BookingsRecapTable = <
  T extends BookingRecapResponseModel | CollectiveBookingResponseModel
>({
  bookingsRecap,
  isLoading,
  locationState,
  audience,
}: IBookingsRecapTableProps<T>) => {
  const [filteredBookings, setFilteredBookings] = useState(bookingsRecap)
  const [currentPage, setCurrentPage] = useState(FIRST_PAGE_INDEX)

  const [filters, setFilters] = useState<BookingsFilters>({
    bookingBeneficiary: EMPTY_FILTER_VALUE,
    bookingToken: EMPTY_FILTER_VALUE,
    offerISBN: EMPTY_FILTER_VALUE,
    offerName: EMPTY_FILTER_VALUE,
    bookingStatus: locationState?.statuses.length
      ? locationState.statuses
      : [...ALL_BOOKING_STATUS],
    selectedOmniSearchCriteria: DEFAULT_OMNISEARCH_CRITERIA,
    keywords: '',
    bookingInstitution: EMPTY_FILTER_VALUE,
  })

  useEffect(() => {
    applyFilters()
  }, [bookingsRecap])

  const updateCurrentPage = (currentPage: number) => {
    setCurrentPage(currentPage)
  }

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
    setCurrentPage(FIRST_PAGE_INDEX)
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

  const columns: (Column<T> & {
    className?: string
  })[] = useMemo(
    () =>
      getColumnsByAudience(
        filters.bookingStatus,
        bookingsRecap,
        updateGlobalFilters,
        audience
      ),
    []
  )

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
          />
          <TableWrapper
            columns={columns}
            currentPage={currentPage}
            data={filteredBookings}
            nbBookings={nbBookings}
            nbBookingsPerPage={NB_BOOKINGS_PER_PAGE}
            updateCurrentPage={updateCurrentPage}
            audience={audience}
          />
        </Fragment>
      ) : (
        <NoFilteredBookings resetFilters={resetAllFilters} />
      )}
    </div>
  )
}

export default BookingsRecapTable
