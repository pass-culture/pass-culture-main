import { useEffect, useState } from 'react'

import type { BookingRecapResponseModel } from '@/apiClient/v1'
import { useAnalytics } from '@/app/App/analytics/firebase'
import { Events } from '@/commons/core/FirebaseEvents/constants'
import { SortingMode, useColumnSorting } from '@/commons/hooks/useColumnSorting'
import { usePagination } from '@/commons/hooks/usePagination'
import type { BookingsFilters } from '@/components/Bookings/BookingsRecapTable/types'
import {
  sortByBeneficiaryName,
  sortByBookingDate,
  sortByOfferName,
} from '@/components/Bookings/BookingsRecapTable/utils/sortingFunctions'
import { Pagination } from '@/ui-kit/Pagination/Pagination'
import { Table, TableVariant } from '@/ui-kit/Table/Table'

import styles from './BookingsTable.module.scss'
import { useBookingsTableColumnsByIndex } from './ColumnsIndividualBooking'

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
    case null:
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
  const { currentSortingColumn, currentSortingMode } =
    useColumnSorting<IndividualBookingsSortingColumn>()

  const sortedBookings = sortBookings(
    bookings,
    currentSortingColumn,
    currentSortingMode
  ).map(
    (b, i) =>
      ({ ...(b as object), id: i }) as BookingRecapResponseModel & {
        id: number
      }
  )

  const { page, setPage, previousPage, nextPage, pageCount, currentPageItems } =
    usePagination(sortedBookings, BOOKINGS_PER_PAGE)

  useEffect(() => {
    setPage(1)
  }, [bookings, setPage])

  const { logEvent } = useAnalytics()

  const [expanded, setExpanded] = useState<Set<number>>(new Set())

  const toggle = (i: string | number) =>
    setExpanded((prev) => {
      const numeric = typeof i === 'string' ? parseInt(i, 10) : i
      const next = new Set(prev)
      next.has(numeric) ? next.delete(numeric) : next.add(numeric)
      return next
    })

  const { columns, getFullRowContentIndividual } =
    useBookingsTableColumnsByIndex({
      bookings: sortedBookings,
      bookingStatuses,
      updateGlobalFilters: updateGlobalFilters,
      expandedIds: expanded,
      onToggle: toggle,
    })

  return (
    <div className={styles['table-wrapper']}>
      <Table
        columns={columns}
        data={currentPageItems}
        isLoading={false}
        variant={TableVariant.COLLAPSE}
        noResult={{
          message: 'Aucune réservation trouvée pour votre recherche',
          subtitle:
            'Vous pouvez modifier vos filtres et lancer une nouvelle recherche ou',
          resetMessage: 'Afficher toutes les réservations',
          onFilterReset: resetFilters,
        }}
        noData={{
          hasNoData: false,
          message: {
            icon: 'strokeNoBookingIcon',
            title: 'Vous n’avez aucune réservation pour le moment',
            subtitle: '',
          },
        }}
        getFullRowContent={getFullRowContentIndividual}
      />

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
