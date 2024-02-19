import cn from 'classnames'
import { useEffect } from 'react'

import { BookingRecapResponseModel } from 'apiClient/v1'
import { SortArrow } from 'components/StocksEventList/SortArrow'
import { Events } from 'core/FirebaseEvents/constants'
import { Audience } from 'core/shared'
import useAnalytics from 'hooks/useAnalytics'
import { SortingMode, useColumnSorting } from 'hooks/useColumnSorting'
import { usePagination } from 'hooks/usePagination'
import { BookingsFilters } from 'screens/Bookings/BookingsRecapTable/types'
import {
  sortByBeneficiaryName,
  sortByBookingDate,
  sortByOfferName,
} from 'screens/Bookings/BookingsRecapTable/utils/sortingFunctions'
import { Pagination } from 'ui-kit/Pagination'

import { FilterByBookingStatus } from '../Filters'
import { NoFilteredBookings } from '../NoFilteredBookings/NoFilteredBookings'

import styles from './BookingsTable.module.scss'
import {
  BookingOfferCell,
  BookingIsDuoCell,
  BeneficiaryCell,
  BookingDateCell,
  BookingTokenCell,
} from './Cells'
import { IndividualBookingStatusCell } from './Cells/IndividualBookingStatusCell'

enum IndividualBookingsSortingColumn {
  OFFER_NAME = 'OFFER_NAME',
  BENEFICIARY_NAME = 'BENEFICIARY_NAME',
  BOOKING_DATE = 'BOOKING_DATE',
}
const BOOKINGS_PER_PAGE = 20

const sortBookings = (
  bookings: BookingRecapResponseModel[],
  currentSortingColumn: IndividualBookingsSortingColumn | null,
  sortingMode: SortingMode
) => {
  switch (currentSortingColumn) {
    case IndividualBookingsSortingColumn.OFFER_NAME:
      return bookings.sort(
        (a, b) =>
          sortByOfferName(a, b) * (sortingMode === SortingMode.ASC ? 1 : -1)
      )

    case IndividualBookingsSortingColumn.BENEFICIARY_NAME:
      return bookings.sort(
        (a, b) =>
          sortByBeneficiaryName(a, b) *
          (sortingMode === SortingMode.ASC ? 1 : -1)
      )

    case IndividualBookingsSortingColumn.BOOKING_DATE:
      return bookings.sort(
        (a, b) =>
          sortByBookingDate(a, b) * (sortingMode === SortingMode.ASC ? 1 : -1)
      )
    default:
      return bookings.sort((a, b) => sortByBookingDate(a, b) * -1)
  }
}

export interface IndividualBookingsTableProps {
  bookings: BookingRecapResponseModel[]
  bookingStatuses: string[]
  updateGlobalFilters: (updatedFilters: Partial<BookingsFilters>) => void
  resetFilters: () => void
}

export const IndividualBookingsTable = ({
  bookings,
  bookingStatuses,
  updateGlobalFilters,
  resetFilters,
}: IndividualBookingsTableProps): JSX.Element => {
  const { currentSortingColumn, currentSortingMode, onColumnHeaderClick } =
    useColumnSorting<IndividualBookingsSortingColumn>()

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
      {currentPageItems.length !== 0 && (
        <table className={styles['table']}>
          <thead>
            <tr>
              <th
                scope="col"
                className={cn(
                  styles['table-header'],
                  styles['column-offer-name']
                )}
              >
                <span>Nom de l’offre</span>

                <SortArrow
                  onClick={() =>
                    onColumnHeaderClick(
                      IndividualBookingsSortingColumn.OFFER_NAME
                    )
                  }
                  sortingMode={
                    currentSortingColumn ===
                    IndividualBookingsSortingColumn.OFFER_NAME
                      ? currentSortingMode
                      : SortingMode.NONE
                  }
                />
              </th>

              <th
                scope="col"
                className={cn(
                  styles['table-header'],
                  styles['column-booking-duo']
                )}
              ></th>

              <th
                scope="col"
                className={cn(
                  styles['table-header'],
                  styles['column-beneficiary']
                )}
              >
                <span>Bénéficiaire</span>

                <SortArrow
                  onClick={() =>
                    onColumnHeaderClick(
                      IndividualBookingsSortingColumn.BENEFICIARY_NAME
                    )
                  }
                  sortingMode={
                    currentSortingColumn ===
                    IndividualBookingsSortingColumn.BENEFICIARY_NAME
                      ? currentSortingMode
                      : SortingMode.NONE
                  }
                />
              </th>

              <th
                scope="col"
                className={cn(
                  styles['table-header'],
                  styles['column-booking-date']
                )}
              >
                <span>Réservation</span>

                <SortArrow
                  onClick={() =>
                    onColumnHeaderClick(
                      IndividualBookingsSortingColumn.BOOKING_DATE
                    )
                  }
                  sortingMode={
                    currentSortingColumn ===
                    IndividualBookingsSortingColumn.BOOKING_DATE
                      ? currentSortingMode
                      : SortingMode.NONE
                  }
                />
              </th>

              <th
                scope="col"
                className={cn(
                  styles['table-header'],
                  styles['column-booking-token']
                )}
              >
                Contremarque
              </th>

              <th
                scope="col"
                className={cn(
                  styles['table-header'],
                  styles['column-booking-status']
                )}
              >
                <FilterByBookingStatus
                  bookingStatuses={bookingStatuses}
                  bookingsRecap={bookings}
                  updateGlobalFilters={updateGlobalFilters}
                  audience={Audience.INDIVIDUAL}
                />
              </th>
            </tr>
          </thead>

          <tbody className={styles['table-body']}>
            {currentPageItems.map((booking, index) => (
              <tr className={styles['table-row']} key={index}>
                <td
                  className={cn(
                    styles['table-cell'],
                    styles['column-offer-name']
                  )}
                >
                  <BookingOfferCell booking={booking} />
                </td>

                <td
                  className={cn(
                    styles['table-cell'],
                    styles['column-booking-duo']
                  )}
                >
                  <BookingIsDuoCell isDuo={booking.bookingIsDuo} />
                </td>

                <td
                  className={cn(
                    styles['table-cell'],
                    styles['column-beneficiary']
                  )}
                >
                  <BeneficiaryCell beneficiaryInfos={booking.beneficiary} />
                </td>

                <td
                  className={cn(
                    styles['table-cell'],
                    styles['column-booking-date']
                  )}
                >
                  <BookingDateCell
                    bookingDateTimeIsoString={booking.bookingDate}
                  />
                </td>

                <td
                  className={cn(
                    styles['table-cell'],
                    styles['column-booking-token']
                  )}
                >
                  <BookingTokenCell bookingToken={booking.bookingToken} />
                </td>

                <td
                  className={cn(
                    styles['table-cell'],
                    styles['column-booking-status']
                  )}
                >
                  <IndividualBookingStatusCell booking={booking} />
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}

      {currentPageItems.length === 0 && (
        <NoFilteredBookings resetFilters={resetFilters} />
      )}

      <Pagination
        currentPage={page}
        pageCount={pageCount}
        onPreviousPageClick={() => {
          previousPage()
          logEvent?.(Events.CLICKED_PAGINATION_PREVIOUS_PAGE, {
            from: location.pathname,
          })
        }}
        onNextPageClick={() => {
          nextPage()
          logEvent?.(Events.CLICKED_PAGINATION_NEXT_PAGE, {
            from: location.pathname,
          })
        }}
      />
    </div>
  )
}
