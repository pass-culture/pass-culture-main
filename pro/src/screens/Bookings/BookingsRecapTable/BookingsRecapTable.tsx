import React, { Fragment, useEffect, useMemo, useState } from 'react'
import type { Column } from 'react-table'

import {
  BookingRecapResponseModel,
  CollectiveBookingResponseModel,
} from 'apiClient/v1'
import { Audience } from 'core/shared'

import {
  BeneficiaryCell,
  BookingTokenCell,
  BookingStatusCell,
  BookingOfferCell,
  BookingIsDuoCell,
  BookingDateCell,
  FilterByOmniSearch,
  Header,
  NoFilteredBookings,
  FilterByBookingStatus,
  ALL_BOOKING_STATUS,
  DEFAULT_OMNISEARCH_CRITERIA,
  EMPTY_FILTER_VALUE,
  TableWrapper,
} from './components'
import DetailsButtonCell from './components/CellsFormatter/DetailsButtonCell'
import InstitutionCell from './components/CellsFormatter/InstitutionCell'
import NumberOfTicketsAndPriceCell from './components/CellsFormatter/NumberOfTicketsAndPriceCell'
import { NB_BOOKINGS_PER_PAGE } from './constants'
import { BookingsFilters } from './types'
import {
  filterBookingsRecap,
  sortByBeneficiaryName,
  sortByBookingDate,
  sortByInstitutionName,
  sortByOfferName,
} from './utils'

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

// TODO: return columns depending on audience
const getColumnsByAudience = <
  T extends BookingRecapResponseModel | CollectiveBookingResponseModel
>(
  bookingStatus: string[],
  bookingsRecap: T[],
  updateGlobalFilters: (updatedFilters: Partial<BookingsFilters>) => void,
  audience: Audience
): (Column<T> & {
  className?: string
})[] => {
  type IndividualColumnType = Column<BookingRecapResponseModel> & {
    className?: string
  }
  type CollectiveColumnType = Column<CollectiveBookingResponseModel> & {
    className?: string
  }

  const offerColumn: IndividualColumnType = {
    id: 'stock',
    accessor: 'stock',
    Header: "Nom de l'offre",
    Cell: ({ value }) => <BookingOfferCell offer={value} />,
    defaultCanSort: true,
    sortType: sortByOfferName,
    className: 'column-offer-name',
  }

  const beneficiaryColumn: IndividualColumnType = {
    Header: 'Bénéficiaire',
    id: 'beneficiary',
    accessor: 'beneficiary',
    Cell: ({ value }) => <BeneficiaryCell beneficiaryInfos={value} />,
    defaultCanSort: true,
    sortType: sortByBeneficiaryName,
    className: 'column-beneficiary',
  }

  const institutionColumn: Column<CollectiveBookingResponseModel> & {
    className?: string
  } = {
    Header: 'Établissement',
    id: 'institution',
    accessor: 'institution',
    Cell: ({ value }) => <InstitutionCell institution={value} />,
    defaultCanSort: true,
    sortType: sortByInstitutionName,
    className: 'column-institution',
  }

  const isDuoColumn: IndividualColumnType = {
    id: 'booking_is_duo',
    accessor: 'booking_is_duo',
    Header: '',
    Cell: ({ value }) => <BookingIsDuoCell isDuo={value} />,
    disableSortBy: true,
    className: 'column-booking-duo',
  }

  const bookingDateColumn: IndividualColumnType = {
    Header: 'Réservation',
    id: 'booking_date',
    accessor: 'booking_date',
    Cell: ({ value }) => <BookingDateCell bookingDateTimeIsoString={value} />,
    defaultCanSort: true,
    sortType: sortByBookingDate,
    className: 'column-booking-date',
  }

  const bookingTokenColumn: IndividualColumnType = {
    Header: 'Contremarque',
    id: 'booking_token',
    accessor: 'booking_token',
    Cell: ({ value }) => <BookingTokenCell bookingToken={value} />,
    disableSortBy: true,
    className: 'column-booking-token',
  }
  const bookingStatusColumn: IndividualColumnType = {
    id: 'booking_status',
    accessor: 'booking_status',
    Cell: ({ row }) => {
      return <BookingStatusCell bookingRecapInfo={row} />
    },
    disableSortBy: true,
    Header: () => (
      <FilterByBookingStatus
        bookingStatuses={bookingStatus}
        bookingsRecap={bookingsRecap}
        updateGlobalFilters={updateGlobalFilters}
      />
    ),
    className: 'column-booking-status',
  }

  const numberOfTicketsAndPriceColumn: CollectiveColumnType = {
    id: 'booking_amount',
    accessor: 'booking_amount',
    Cell: ({ row }) => <NumberOfTicketsAndPriceCell bookingRecapInfo={row} />,
    Header: 'Places et prix',
    disableSortBy: true,
  }

  const detailsColumn: CollectiveColumnType = {
    id: 'booking_details',
    accessor: 'booking_amount',
    Cell: ({ row }) => <DetailsButtonCell bookingRow={row} />,
    Header: '',
    disableSortBy: true,
  }

  const individualBookingsColumns = [
    offerColumn,
    isDuoColumn,
    beneficiaryColumn,
    bookingDateColumn,
    bookingTokenColumn,
    bookingStatusColumn,
  ]

  const collectiveBookingsColumns = [
    offerColumn,
    institutionColumn,
    numberOfTicketsAndPriceColumn,
    bookingStatusColumn,
    detailsColumn,
  ]
  return (
    audience === Audience.INDIVIDUAL
      ? individualBookingsColumns
      : collectiveBookingsColumns
  ) as (Column<T> & {
    className?: string
  })[]
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
