import { useState } from 'react'

import type { BookingRecapResponseModel } from '@/apiClient/v1'
import { useAnalytics } from '@/app/App/analytics/firebase'
import { Events } from '@/commons/core/FirebaseEvents/constants'
import { usePagination } from '@/commons/hooks/usePagination'
import strokeNoBookingIcon from '@/icons/stroke-no-booking.svg'
import { Pagination } from '@/ui-kit/Pagination/Pagination'
import { Table, TableVariant } from '@/ui-kit/Table/Table'

import type { BookingsFilters } from '../Components/types'
import { useBookingsTableColumnsByIndex } from './ColumnsIndividualBooking'
import styles from './IndividualBookingsTable.module.scss'

const BOOKINGS_PER_PAGE = 20
interface IndividualBookingsTableProps {
  bookings: BookingRecapResponseModel[]
  bookingStatuses: string[]
  updateGlobalFilters: (updatedFilters: Partial<BookingsFilters>) => void
  resetFilters: () => void
  isLoading: boolean
  hasNoBooking: boolean
}

export const IndividualBookingsTable = ({
  bookings,
  bookingStatuses,
  updateGlobalFilters,
  resetFilters,
  isLoading,
  hasNoBooking,
}: IndividualBookingsTableProps): JSX.Element => {
  const bookingsWithIds = bookings.map(
    (b, i) =>
      ({ ...(b as object), id: i }) as BookingRecapResponseModel & {
        id: number
      }
  )

  const { page, previousPage, nextPage, pageCount, currentPageItems } =
    usePagination(bookingsWithIds, BOOKINGS_PER_PAGE)

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
      bookings: bookingsWithIds,
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
          hasNoData: hasNoBooking,
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
