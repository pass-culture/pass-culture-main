import cn from 'classnames'
import React, { useEffect } from 'react'

import { CollectiveBookingResponseModel } from 'apiClient/v1'
import { useAnalytics } from 'app/App/analytics/firebase'
import { SortArrow } from 'components/StocksEventList/SortArrow'
import { Events } from 'core/FirebaseEvents/constants'
import { Audience } from 'core/shared/types'
import { SortingMode, useColumnSorting } from 'hooks/useColumnSorting'
import { usePagination } from 'hooks/usePagination'
import { BookingsFilters } from 'screens/Bookings/BookingsRecapTable/types'
import {
  sortByBookingDate,
  sortByInstitutionName,
  sortByOfferName,
} from 'screens/Bookings/BookingsRecapTable/utils/sortingFunctions'
import { Pagination } from 'ui-kit/Pagination/Pagination'

import { FilterByBookingStatus } from '../Filters/FilterByBookingStatus'
import { NoFilteredBookings } from '../NoFilteredBookings/NoFilteredBookings'

import styles from './BookingsTable.module.scss'
import { CollectiveTableRow } from './CollectiveTableRow'

enum CollectiveBookingsSortingColumn {
  OFFER_NAME = 'OFFER_NAME',
  INSTITUTION_NAME = 'INSTITUTION_NAME',
  BENEFICIARY_NAME = 'BENEFICIARY_NAME',
  BOOKING_DATE = 'BOOKING_DATE',
}
const BOOKINGS_PER_PAGE = 20

const sortBookings = (
  bookings: CollectiveBookingResponseModel[],
  currentSortingColumn: CollectiveBookingsSortingColumn | null,
  sortingMode: SortingMode
) => {
  switch (currentSortingColumn) {
    case CollectiveBookingsSortingColumn.OFFER_NAME:
      return bookings.sort(
        (a, b) =>
          sortByOfferName(a, b) * (sortingMode === SortingMode.ASC ? 1 : -1)
      )

    case CollectiveBookingsSortingColumn.INSTITUTION_NAME:
      return bookings.sort(
        (a, b) =>
          sortByInstitutionName(a, b) *
          (sortingMode === SortingMode.ASC ? 1 : -1)
      )
    default:
      return bookings.sort((a, b) => sortByBookingDate(a, b) * -1)
  }
}

interface CollectiveBookingsTableProps {
  bookings: CollectiveBookingResponseModel[]
  bookingStatuses: string[]
  updateGlobalFilters: (updatedFilters: Partial<BookingsFilters>) => void
  defaultOpenedBookingId: string
  resetFilters: () => void
}

export const CollectiveBookingsTable = ({
  bookings,
  bookingStatuses,
  updateGlobalFilters,
  defaultOpenedBookingId,
  resetFilters,
}: CollectiveBookingsTableProps): JSX.Element => {
  const { currentSortingColumn, currentSortingMode, onColumnHeaderClick } =
    useColumnSorting<CollectiveBookingsSortingColumn>()

  const sortedBookings = sortBookings(
    bookings,
    currentSortingColumn,
    currentSortingMode
  )
  const { page, setPage, previousPage, nextPage, pageCount, currentPageItems } =
    usePagination(sortedBookings, BOOKINGS_PER_PAGE)

  useEffect(() => {
    setPage(1)
  }, [bookings, setPage])

  const { logEvent } = useAnalytics()

  return (
    <div className={styles['table-wrapper']}>
      <table className={styles['table']}>
        <caption className="visually-hidden">Liste des réservations</caption>

        <thead className={styles['table-header']}>
          <tr className={styles['table-header-row']}>
            <th
              scope="col"
              className={cn(
                styles['column-booking-id'],
                styles['table-header-cell']
              )}
            >
              Réservation
            </th>

            <th
              scope="col"
              className={cn(
                styles['column-offer-name'],
                styles['table-header-cell']
              )}
            >
              <span>Nom de l’offre</span>

              <SortArrow
                onClick={() =>
                  onColumnHeaderClick(
                    CollectiveBookingsSortingColumn.OFFER_NAME
                  )
                }
                sortingMode={
                  currentSortingColumn ===
                  CollectiveBookingsSortingColumn.OFFER_NAME
                    ? currentSortingMode
                    : SortingMode.NONE
                }
              />
            </th>

            <th
              scope="col"
              className={cn(
                styles['column-institution'],
                styles['table-header-cell']
              )}
            >
              <span>Établissement</span>

              <SortArrow
                onClick={() =>
                  onColumnHeaderClick(
                    CollectiveBookingsSortingColumn.INSTITUTION_NAME
                  )
                }
                sortingMode={
                  currentSortingColumn ===
                  CollectiveBookingsSortingColumn.INSTITUTION_NAME
                    ? currentSortingMode
                    : SortingMode.NONE
                }
              />
            </th>

            <th
              scope="col"
              className={cn(
                styles['column-price-and-price'],
                styles['table-header-cell']
              )}
            >
              Places et prix
            </th>

            <th
              scope="col"
              className={cn(
                styles['column-booking-status'],
                styles['table-header-cell']
              )}
            >
              <FilterByBookingStatus
                bookingStatuses={bookingStatuses}
                bookingsRecap={bookings}
                updateGlobalFilters={updateGlobalFilters}
                audience={Audience.COLLECTIVE}
              />
            </th>

            <th scope="col">
              <span className="visually-hidden">Détails</span>
            </th>
          </tr>
        </thead>

        <tbody className={styles['table-body']}>
          {currentPageItems.map((booking) => (
            <CollectiveTableRow
              booking={booking}
              key={booking.bookingId}
              defaultOpenedBookingId={defaultOpenedBookingId}
            />
          ))}
        </tbody>
      </table>

      {currentPageItems.length === 0 && (
        <NoFilteredBookings resetFilters={resetFilters} />
      )}

      <Pagination
        currentPage={page}
        pageCount={pageCount}
        onPreviousPageClick={() => {
          previousPage()
          logEvent(Events.CLICKED_PAGINATION_PREVIOUS_PAGE, {
            from: location.pathname,
          })
        }}
        onNextPageClick={() => {
          nextPage()
          logEvent(Events.CLICKED_PAGINATION_NEXT_PAGE, {
            from: location.pathname,
          })
        }}
      />
    </div>
  )
}
