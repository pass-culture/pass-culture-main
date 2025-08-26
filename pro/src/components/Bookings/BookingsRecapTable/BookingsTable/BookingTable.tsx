import {
  BookingRecapResponseModel,
  CollectiveBookingResponseModel,
} from '@/apiClient/v1'
import { Audience } from '@/commons/core/shared/types'
import strokeNoBooking from '@/icons/stroke-no-booking.svg'
import { Column, Table, TableVariant } from '@/ui-kit/Table/Table'
import { ReactNode, useEffect, useMemo, useState } from 'react'
import { BookingsFilters } from '../types'
import styles from './BookingsTable.module.scss'
import { useCollectiveBookingsColumns } from './ColumnsCollectiveBooking'
import { useBookingsTableColumnsByIndex } from './ColumnsIndividualBooking'

type AnyBooking = BookingRecapResponseModel | CollectiveBookingResponseModel

type Props<T extends AnyBooking> = {
  audience: Audience
  isLoading: boolean
  /** filtered bookings to display */
  bookings: T[]
  /** source bookings list for header/columns context (usually the unfiltered list) */
  allBookings: T[]
  bookingStatuses: string[]
  onUpdateGlobalFilters?: (updated: Partial<BookingsFilters>) => void
  onResetAllFilters?: () => void
  /** bookingId from URL to open by default (if present) */
  defaultBookingId?: string
}

export function BookingsTable<T extends AnyBooking>({
  audience,
  isLoading,
  bookings,
  allBookings,
  bookingStatuses,
  onUpdateGlobalFilters,
  onResetAllFilters,
  defaultBookingId,
}: Props<T>) {
  // Map to table rows with a stable numeric id (index-based)
  const rows = useMemo(
    () =>
      bookings.map(
        (b, i) =>
          ({ ...(b as object), id: i }) as T & {
            id: number
          }
      ),
    [bookings]
  )

  // Expand/collapse state by row index
  const [expanded, setExpanded] = useState<Set<number>>(new Set())

  // When bookings or defaultBookingId change, open the row matching that bookingId if found
  useEffect(() => {
    if (!defaultBookingId) {
      setExpanded(new Set())
      return
    }
    const idx = bookings.findIndex(
      (b: any) => String(b.bookingId) === String(defaultBookingId)
    )
    setExpanded(idx >= 0 ? new Set([idx]) : new Set())
  }, [bookings, defaultBookingId])

  const toggle = (i: string | number) =>
    setExpanded((prev) => {
      const numeric = typeof i === 'string' ? parseInt(i, 10) : i
      const next = new Set(prev)
      next.has(numeric) ? next.delete(numeric) : next.add(numeric)
      return next
    })

  // Columns by audience
  const { columns: individualColumns, getFullRowContentIndividual } =
    useBookingsTableColumnsByIndex({
      bookings: allBookings as BookingRecapResponseModel[],
      bookingStatuses,
      updateGlobalFilters: onUpdateGlobalFilters,
      expandedIds: expanded,
      onToggle: toggle,
    })

  const { columns: collectiveColumns, getFullRowContentCollective } =
    useCollectiveBookingsColumns({
      bookings: allBookings as CollectiveBookingResponseModel[], // context list
      bookingStatuses,
      updateGlobalFilters: onUpdateGlobalFilters,
      expandedIds: expanded,
      onToggle: toggle,
    })

  const tableTitle =
    audience === Audience.COLLECTIVE
      ? 'Réservations collectives'
      : 'Réservations individuelles'

  return (
    <div className={styles['table-wrapper']}>
      <Table
        title={tableTitle}
        columns={
          audience === Audience.INDIVIDUAL
            ? (individualColumns as unknown as Column<T & { id: number }>[])
            : (collectiveColumns as unknown as Column<T & { id: number }>[])
        }
        data={rows}
        isLoading={isLoading}
        variant={TableVariant.COLLAPSE}
        noData={{
          hasNoData: bookings.length === 0,
          message: {
            icon: strokeNoBooking,
            title: 'Vous n’avez pas encore de réservations',
            subtitle: '',
          },
        }}
        noResult={{
          message: 'Aucune réservation trouvée pour votre recherche',
          resetMessage: 'Afficher toutes les réservations',
          onFilterReset: onResetAllFilters,
        }}
        getFullRowContent={
          audience === Audience.INDIVIDUAL
            ? (getFullRowContentIndividual as unknown as (
                row: T & { id: number }
              ) => ReactNode)
            : (getFullRowContentCollective as unknown as (
                row: T & { id: number }
              ) => ReactNode)
        }
      />
    </div>
  )
}
