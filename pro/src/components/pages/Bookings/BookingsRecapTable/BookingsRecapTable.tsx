import React, { Fragment, useEffect, useState } from 'react'
import type { Cell } from 'react-table'

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

type CustomCellValue<
  T extends BookingRecapResponseModel | CollectiveBookingResponseModel,
  K extends keyof T
> = T[K]

type BookingsFilters = {
  bookingBeneficiary: string
  bookingToken: string
  offerISBN: string
  offerName: string
  bookingStatus: string[]
  selectedOmniSearchCriteria: string
  keywords: string
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

  const columns = [
    {
      id: 1,
      headerTitle: "Nom de l'offre",
      accessor: 'stock',
      Cell: ({ value }: Cell<{ stock: CustomCellValue<T, 'stock'> }>) => (
        <BookingOfferCell offer={value} />
      ),
      className: 'column-offer-name',
      defaultCanSort: true,
      sortType: sortByOfferName,
    },
    {
      id: 2,
      headerTitle: '',
      accessor: 'booking_is_duo',
      Cell: ({
        value,
      }: Cell<{ booking_is_duo: CustomCellValue<T, 'booking_is_duo'> }>) => (
        <BookingIsDuoCell isDuo={value} />
      ),
      className: 'column-booking-duo',
      disableSortBy: true,
    },
    {
      id: 3,
      headerTitle: 'Bénéficiaire',
      accessor: 'beneficiary',
      Cell: ({
        value,
      }: Cell<{ beneficiary: CustomCellValue<T, 'beneficiary'> }>) => (
        <BeneficiaryCell beneficiaryInfos={value} />
      ),
      className: 'column-beneficiary',
      defaultCanSort: true,
      sortType: sortByBeneficiaryName,
    },
    {
      id: 4,
      headerTitle: 'Réservation',
      accessor: 'booking_date',
      Cell: ({
        value,
      }: Cell<{ booking_date: CustomCellValue<T, 'booking_date'> }>) => (
        <BookingDateCell bookingDateTimeIsoString={value} />
      ),
      className: 'column-booking-date',
      defaultCanSort: true,
      sortType: sortByBookingDate,
    },
    {
      id: 5,
      headerTitle: 'Contremarque',
      accessor: 'booking_token',
      Cell: ({
        value,
      }: Cell<{ booking_token: CustomCellValue<T, 'booking_token'> }>) => (
        <BookingTokenCell bookingToken={value} />
      ),
      className: 'column-booking-token',
      disableSortBy: true,
    },
    {
      id: 6,
      accessor: 'booking_status',
      Cell: ({
        row,
      }: Cell<{ booking_status: CustomCellValue<T, 'booking_status'> }>) => {
        return <BookingStatusCell bookingRecapInfo={row} />
      },
      className: 'column-booking-status',
      disableSortBy: true,
      HeaderTitleFilter: () => (
        <FilterByBookingStatus
          bookingStatuses={filters.bookingStatus}
          bookingsRecap={filteredBookings}
          updateGlobalFilters={updateGlobalFilters}
        />
      ),
    },
  ]

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

  const updateGlobalFilters = (updatedFilters: BookingsFilters) => {
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
