import { useState } from 'react'

import type { BookingRecapResponseModel } from '@/apiClient/v1'
import { useAnalytics } from '@/app/App/analytics/firebase'
import { Events } from '@/commons/core/FirebaseEvents/constants'
import { useAccessibleScroll } from '@/commons/hooks/useAccessibleScroll'
import type { SortingMode } from '@/commons/hooks/useColumnSorting'
import { AccessibleScrollContainer } from '@/components/AccessibleScrollContainer/AccessibleScrollContainer'
import strokeNoBookingIcon from '@/icons/stroke-no-booking.svg'
import { Table, TableVariant } from '@/ui-kit/Table/Table'

import type { BookingsFilters } from '../Components/types'
import { useBookingsTableColumnsByIndex } from './ColumnsIndividualBooking'

interface IndividualBookingsTableProps {
  bookings: BookingRecapResponseModel[]
  bookingStatuses: string[]
  updateGlobalFilters: (updatedFilters: Partial<BookingsFilters>) => void
  resetFilters: () => void
  isLoading: boolean
  hasNoBooking: boolean
  currentPage: number
  pageCount: number
  onPageChange: (page: number) => void
  onSortChange?: (column: string | null, order: SortingMode) => void
}

export const IndividualBookingsTable = ({
  bookings,
  bookingStatuses,
  updateGlobalFilters,
  resetFilters,
  isLoading,
  hasNoBooking,
  currentPage,
  pageCount,
  onPageChange,
  onSortChange,
}: IndividualBookingsTableProps): JSX.Element => {
  const bookingsWithIds = bookings.map(
    (b, i) =>
      ({ ...(b as object), id: i }) as BookingRecapResponseModel & {
        id: number
      }
  )

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

  const { contentWrapperRef, scrollToContentWrapper } = useAccessibleScroll({
    selector: '#content-wrapper',
  })

  return (
    <AccessibleScrollContainer
      containerRef={contentWrapperRef}
      liveMessage={`Page ${currentPage} sur ${pageCount}`}
    >
      <Table
        columns={columns}
        data={bookingsWithIds}
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
        pagination={{
          currentPage: currentPage,
          pageCount: pageCount,
          onPageClick: (newPage) => {
            onPageChange(newPage)
            scrollToContentWrapper()

            if (currentPage + 1 === newPage) {
              logEvent(Events.CLICKED_PAGINATION_NEXT_PAGE, {
                from: location.pathname,
              })
            } else if (currentPage - 1 === newPage) {
              logEvent(Events.CLICKED_PAGINATION_PREVIOUS_PAGE, {
                from: location.pathname,
              })
            }
          },
        }}
        getFullRowContent={getFullRowContentIndividual}
        onSortChange={onSortChange}
      />
    </AccessibleScrollContainer>
  )
}
