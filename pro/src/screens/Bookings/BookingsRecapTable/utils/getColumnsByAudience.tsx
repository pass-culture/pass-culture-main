import React from 'react'
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
import BookingIdCell from '../components/CellsFormatter/BookingIdCell'
import { BookingsFilters } from '../types'

import styles from './Column.module.scss'
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

  const bookingIdColumn: CollectiveColumnType = {
    id: 'bookingId',
    accessor: 'bookingId',
    Cell: ({ value }) => <BookingIdCell id={value} />,
    Header: 'Réservation',
    className: styles['column-booking-id'],
  }

  const offerColumn: IndividualColumnType = {
    id: 'stock',
    accessor: 'stock',
    Header: 'Nom de l’offre',
    Cell: ({ value, row }) => (
      <BookingOfferCell
        offer={value}
        isCollective={audience !== Audience.INDIVIDUAL}
        bookingRecapInfo={row}
      />
    ),
    defaultCanSort: true,
    sortType: sortByOfferName,
    className:
      audience === Audience.INDIVIDUAL
        ? styles['column-offer-name']
        : styles['column-collective-offer-name'],
  }

  const beneficiaryColumn: IndividualColumnType = {
    Header: 'Bénéficiaire',
    id: 'beneficiary',
    accessor: 'beneficiary',
    Cell: ({ value }) => <BeneficiaryCell beneficiaryInfos={value} />,
    defaultCanSort: true,
    sortType: sortByBeneficiaryName,
    className: styles['column-beneficiary'],
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
    className: styles['column-institution'],
  }

  const isDuoColumn: IndividualColumnType = {
    id: 'bookingIsDuo',
    accessor: 'bookingIsDuo',
    Header: '',
    Cell: ({ value }) => <BookingIsDuoCell isDuo={value} />,
    disableSortBy: true,
    className: styles['column-booking-duo'],
  }

  const bookingDateColumn: IndividualColumnType = {
    Header: 'Réservation',
    id: 'bookingDate',
    accessor: 'bookingDate',
    Cell: ({ value }) => <BookingDateCell bookingDateTimeIsoString={value} />,
    defaultCanSort: true,
    sortType: sortByBookingDate,
    className: styles['column-booking-date'],
  }

  const bookingTokenColumn: IndividualColumnType = {
    Header: 'Contremarque',
    id: 'bookingToken',
    accessor: 'bookingToken',
    Cell: ({ value }) => <BookingTokenCell bookingToken={value} />,
    disableSortBy: true,
    className: styles['column-booking-token'],
  }
  const bookingStatusColumn: IndividualColumnType = {
    id: 'bookingStatus',
    accessor: 'bookingStatus',
    Cell: ({ row }) => {
      return (
        <BookingStatusCell
          bookingRecapInfo={row}
          isCollectiveStatus={audience !== Audience.INDIVIDUAL}
        />
      )
    },
    disableSortBy: true,
    Header: () => (
      <FilterByBookingStatus
        bookingStatuses={bookingStatus}
        bookingsRecap={bookingsRecap}
        updateGlobalFilters={updateGlobalFilters}
        audience={audience}
      />
    ),
    className: styles['column-booking-status'],
  }

  const numberOfTicketsAndPriceColumn: CollectiveColumnType = {
    id: 'bookingAmount',
    accessor: 'bookingAmount',
    Cell: ({ row }) => <NumberOfTicketsAndPriceCell bookingRecapInfo={row} />,
    Header: 'Places et prix',
    disableSortBy: true,
    className: styles['column-price-and-price'],
  }

  const detailsColumn: CollectiveColumnType = {
    id: 'bookingDetails',
    accessor: 'bookingAmount',
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
    bookingIdColumn,
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
