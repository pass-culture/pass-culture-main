import React, { Fragment, useEffect, useState } from 'react'
import type { Column } from 'react-table'

import {
  BookingRecapResponseModel,
  CollectiveBookingResponseModel,
} from 'apiClient/v1'

import BeneficiaryCell from './CellsFormatter/BeneficiaryCell'
import BookingDateCell from './CellsFormatter/BookingDateCell'
import BookingIsDuoCell from './CellsFormatter/BookingIsDuoCell'
import BookingOfferCell from './CellsFormatter/BookingOfferCell'
import BookingStatusCell from './CellsFormatter/BookingStatusCell'
import BookingTokenCell from './CellsFormatter/BookingTokenCell'
import {
  ALL_BOOKING_STATUS,
  DEFAULT_OMNISEARCH_CRITERIA,
  EMPTY_FILTER_VALUE,
} from './Filters/_constants'
import FilterByBookingStatus from './Filters/FilterByBookingStatus'
import FilterByOmniSearch from './Filters/FilterByOmniSearch'
import Header from './Header/Header'
import { NB_BOOKINGS_PER_PAGE } from './NB_BOOKINGS_PER_PAGE'
import NoFilteredBookings from './NoFilteredBookings/NoFilteredBookings'
import TableFrame from './Table/TableFrame'
import { BookingsFilters } from './types'
import filterBookingsRecap from './utils/filterBookingsRecap'
import {
  sortByBeneficiaryName,
  sortByBookingDate,
  sortByOfferName,
} from './utils/sortingFunctions'

const FIRST_PAGE_INDEX = 0

interface IBookingsRecapTableProps<
  T extends BookingRecapResponseModel | CollectiveBookingResponseModel
> {
  bookingsRecap: T[]
  isLoading: boolean
  locationState?: {
    statuses: string[]
  }
}

// TODO: return columns depending on audience
const getColumnsByAudience = <
  T extends BookingRecapResponseModel | CollectiveBookingResponseModel
>(
  filters: BookingsFilters,
  bookingsRecap: T[],
  updateGlobalFilters: (updatedFilters: Partial<BookingsFilters>) => void
): (Column<T> & {
  className?: string
})[] => {
  const columns: (Column<BookingRecapResponseModel> & {
    className?: string
  })[] = [
    {
      id: 'stock',
      accessor: 'stock',
      Header: "Nom de l'offre",
      Cell: ({ value }) => <BookingOfferCell offer={value} />,
      defaultCanSort: true,
      sortType: sortByOfferName,
      className: 'column-offer-name',
    },
    {
      id: 'booking_is_duo',
      accessor: 'booking_is_duo',
      Header: '',
      Cell: ({ value }) => <BookingIsDuoCell isDuo={value} />,
      disableSortBy: true,
      className: 'column-booking-duo',
    },
    {
      Header: 'Bénéficiaire',
      id: 'beneficiary',
      accessor: 'beneficiary',
      Cell: ({ value }) => <BeneficiaryCell beneficiaryInfos={value} />,
      defaultCanSort: true,
      sortType: sortByBeneficiaryName,
      className: 'column-beneficiary',
    },
    {
      Header: 'Réservation',
      id: 'booking_date',
      accessor: 'booking_date',
      Cell: ({ value }) => <BookingDateCell bookingDateTimeIsoString={value} />,
      defaultCanSort: true,
      sortType: sortByBookingDate,
      className: 'column-booking-date',
    },
    {
      Header: 'Contremarque',
      id: 'booking_token',
      accessor: 'booking_token',
      Cell: ({ value }) => <BookingTokenCell bookingToken={value} />,
      disableSortBy: true,
      className: 'column-booking-token',
    },
    {
      id: 'booking_status',
      accessor: 'booking_status',
      Cell: ({ row }) => {
        return <BookingStatusCell bookingRecapInfo={row} />
      },
      disableSortBy: true,
      Header: () => (
        <FilterByBookingStatus
          bookingStatuses={filters.bookingStatus}
          bookingsRecap={bookingsRecap}
          updateGlobalFilters={updateGlobalFilters}
        />
      ),
      className: 'column-booking-status',
    },
  ]
  return columns as (Column<T> & {
    className?: string
  })[]
}

const BookingsRecapTable = <
  T extends BookingRecapResponseModel | CollectiveBookingResponseModel
>({
  bookingsRecap,
  isLoading,
  locationState,
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
  })

  useEffect(() => {
    applyFilters()
  }, [bookingsRecap])

  const updateCurrentPage = (currentPage: number) => {
    setCurrentPage(currentPage)
  }

  const updateGlobalFilters = (updatedFilters: Partial<BookingsFilters>) => {
    setFilters(filters => ({
      ...filters,
      ...updatedFilters,
    }))
    applyFilters()
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
      bookingStatus: [...ALL_BOOKING_STATUS],
      keywords: '',
      selectedOmniSearchCriteria: DEFAULT_OMNISEARCH_CRITERIA,
    }
    setFilters(filtersBookingResults)
    applyFilters(filtersBookingResults)
  }

  const updateFilters = (
    updatedFilter: BookingsFilters,
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
  })[] = getColumnsByAudience(filters, bookingsRecap, updateGlobalFilters)

  return (
    <div>
      <div className="filters-wrapper">
        <FilterByOmniSearch
          isDisabled={isLoading}
          keywords={filters.keywords}
          selectedOmniSearchCriteria={filters.selectedOmniSearchCriteria}
          updateFilters={updateFilters}
        />
      </div>
      {nbBookings > 0 ? (
        <Fragment>
          <Header
            bookingsRecapFiltered={filteredBookings}
            isLoading={isLoading}
          />
          <TableFrame
            columns={columns}
            currentPage={currentPage}
            data={filteredBookings}
            nbBookings={nbBookings}
            nbBookingsPerPage={NB_BOOKINGS_PER_PAGE}
            updateCurrentPage={updateCurrentPage}
          />
        </Fragment>
      ) : (
        <NoFilteredBookings resetFilters={resetAllFilters} />
      )}
    </div>
  )
}

export default BookingsRecapTable
