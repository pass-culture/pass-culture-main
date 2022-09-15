import { Column } from 'react-table'

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
  FilterByBookingStatus,
  NumberOfTicketsAndPriceCell,
  DetailsButtonCell,
  InstitutionCell,
} from '../components'
import { BookingsFilters } from '../types'

import {
  sortByBeneficiaryName,
  sortByBookingDate,
  sortByInstitutionName,
  sortByOfferName,
} from './sortingFunctions'

export const getColumnsByAudience = <
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
