import cn from 'classnames'
import { useEffect } from 'react'

import { BookingRecapResponseModel } from 'apiClient/v1'
import { useAnalytics } from 'app/App/analytics/firebase'
import { SortArrow } from 'components/StocksEventList/SortArrow'
import { Events } from 'core/FirebaseEvents/constants'
import { Audience } from 'core/shared/types'
import { SortingMode, useColumnSorting } from 'hooks/useColumnSorting'
import { usePagination } from 'hooks/usePagination'
import strokeDuoIcon from 'icons/stroke-duo.svg'
import { BookingsFilters } from 'screens/Bookings/BookingsRecapTable/types'
import {
  sortByBeneficiaryName,
  sortByBookingDate,
  sortByOfferName,
} from 'screens/Bookings/BookingsRecapTable/utils/sortingFunctions'
import { Pagination } from 'ui-kit/Pagination/Pagination'
import { SvgIcon } from 'ui-kit/SvgIcon/SvgIcon'

import { FilterByBookingStatus } from '../Filters/FilterByBookingStatus'
import { NoFilteredBookings } from '../NoFilteredBookings/NoFilteredBookings'

import styles from './BookingsTable.module.scss'
import { BeneficiaryCell } from './Cells/BeneficiaryCell'
import { BookingDateCell } from './Cells/BookingDateCell'
import { BookingOfferCell } from './Cells/BookingOfferCell'
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
          <thead className={styles['table-header']}>
            <tr>
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
                  styles['column-beneficiary'],
                  styles['table-header-cell']
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
                  styles['column-booking-date'],
                  styles['table-header-cell']
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
                  styles['column-booking-token'],
                  styles['table-header-cell']
                )}
              >
                Contremarque
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
                  data-label="Nom de l’offre"
                >
                  <div
                    className={cn(
                      styles['cell-item-wrapper'],
                      styles['offer-details-wrapper']
                    )}
                  >
                    <BookingOfferCell booking={booking} />

                    {booking.bookingIsDuo && (
                      <SvgIcon
                        src={strokeDuoIcon}
                        alt="Réservation DUO"
                        className={styles['bookings-duo-icon']}
                      />
                    )}
                  </div>
                </td>

                <td
                  className={cn(
                    styles['table-cell'],
                    styles['column-beneficiary']
                  )}
                  data-label="Bénéficiaire"
                >
                  <BeneficiaryCell
                    beneficiaryInfos={booking.beneficiary}
                    className={styles['cell-item-wrapper']}
                  />
                </td>

                <td
                  className={cn(
                    styles['table-cell'],
                    styles['column-booking-date']
                  )}
                  data-label="Réservation"
                >
                  <BookingDateCell
                    bookingDateTimeIsoString={booking.bookingDate}
                    className={styles['cell-item-wrapper']}
                  />
                </td>

                <td
                  className={cn(
                    styles['table-cell'],
                    styles['column-booking-token']
                  )}
                  data-label="Contremarque"
                >
                  <span className={styles['cell-item-wrapper']}>
                    {booking.bookingToken || '-'}
                  </span>
                </td>

                <td
                  className={cn(
                    styles['table-cell'],
                    styles['column-booking-status']
                  )}
                  data-label="Statut"
                >
                  <IndividualBookingStatusCell
                    booking={booking}
                    className={styles['cell-item-wrapper']}
                  />
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
