import { useEffect, useState } from 'react'

import type { BookingRecapResponseModel } from '@/apiClient/v1'
import { useAnalytics } from '@/app/App/analytics/firebase'
import { Events } from '@/commons/core/FirebaseEvents/constants'
import { usePagination } from '@/commons/hooks/usePagination'
import type { BookingsFilters } from '@/components/Bookings/BookingsFilters/types'
import strokeNoBookingIcon from '@/icons/stroke-no-booking.svg'
import { Pagination } from '@/ui-kit/Pagination/Pagination'
import { Table, TableVariant } from '@/ui-kit/Table/Table'

import { useBookingsTableColumnsByIndex } from './ColumnsIndividualBooking'
import styles from './IndividualBookingsTable.module.scss'

const BOOKINGS_PER_PAGE = 20

export interface IndividualBookingsTableProps {
  bookings: BookingRecapResponseModel[]
  bookingStatuses: string[]
  updateGlobalFilters: (updatedFilters: Partial<BookingsFilters>) => void
  resetFilters: () => void
  isLoading: boolean
  hasBookings: boolean
}

export const IndividualBookingsTable = ({
  bookings,
  bookingStatuses,
  updateGlobalFilters,
  resetFilters,
  isLoading,
  hasBookings,
}: IndividualBookingsTableProps): JSX.Element => {
  const bookingsWithId = bookings.map(
    (b, i) =>
      ({ ...(b as object), id: i }) as BookingRecapResponseModel & {
        id: number
      }
  )

  const { page, setPage, previousPage, nextPage, pageCount, currentPageItems } =
    usePagination(bookingsWithId, BOOKINGS_PER_PAGE)

  useEffect(() => {
    setPage(1)
  }, [setPage])

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
      bookings: bookingsWithId,
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
        isLoading={isLoading}
        variant={TableVariant.COLLAPSE}
        noResult={{
          message: 'Aucune réservation trouvée pour votre recherche',
          subtitle:
            'Vous pouvez modifier vos filtres et lancer une nouvelle recherche ou',
          resetMessage: 'Afficher toutes les réservations',
          onFilterReset: resetFilters,
        }}
        noData={{
          hasNoData: !hasBookings,
          message: {
            icon: strokeNoBookingIcon,
            title: 'Vous n’avez aucune réservation pour le moment',
            subtitle: '',
          },
        }}
        getFullRowContent={getFullRowContentIndividual}
      />

      <div className={styles['table-pagination']}>
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
    </div>
  )
}
