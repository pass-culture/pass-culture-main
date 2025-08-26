// useCollectiveBookingsColumns.tsx
import cn from 'classnames'
import useSWR from 'swr'

import { api } from '@/apiClient/api'
import type { CollectiveBookingResponseModel } from '@/apiClient/v1'
import { GET_COLLECTIVE_BOOKING_BY_ID_QUERY_KEY } from '@/commons/config/swrQueryKeys'
// ✅ imports pour l'entête “Statut” en composant
import { Audience } from '@/commons/core/shared/types'
import { formatPrice } from '@/commons/utils/formatPrice'
import { pluralizeString } from '@/commons/utils/pluralize'
import type { BookingsFilters } from '@/components/Bookings/BookingsRecapTable/types'
import { Spinner } from '@/ui-kit/Spinner/Spinner'
import type { Column } from '@/ui-kit/Table/Table'

import { doesUserPreferReducedMotion } from '@/commons/utils/windowMatchMedia'
import { useRef } from 'react'
import { FilterByBookingStatus } from '../Filters/FilterByBookingStatus'
import styles from './BookingsTable.module.scss'
import { BookingOfferCell } from './Cells/BookingOfferCell'
import { CollectiveBookingStatusCell } from './Cells/CollectiveBookingStatusCell'
import { DetailsButtonCell } from './Cells/DetailsButtonCell'
import { CollectiveBookingDetails } from './CollectiveBookingDetails'

// Row pour <Table/> : on ajoute { id } (ex: = bookingId)
export type BookingRow = CollectiveBookingResponseModel & {
  id: string | number
}

type UseCollectiveBookingsColumnsOpts = {
  // ✅ la liste des bookings à passer au header
  bookings: CollectiveBookingResponseModel[]
  bookingStatuses?: string[]
  updateGlobalFilters?: (updated: Partial<BookingsFilters>) => void

  expandedIds?: Set<string | number>
  onToggle?: (id: string | number) => void
}

const institutionName = (b: BookingRow) =>
  `${b.institution.institutionType ?? ''} ${b.institution.name ?? ''}`.trim()

const institutionAddress = (b: BookingRow) =>
  `${b.institution.postalCode ?? ''} ${b.institution.city ?? ''}`.trim()

const sortInstitution = (b: BookingRow) => {
  const name = b.institution?.name || ''
  const type = b.institution?.institutionType || ''
  const city = b.institution?.city || ''
  return `${name} ${type} ${city}`.toLocaleLowerCase()
}

// Loader SWR pour la ligne de détails plein-largeur
function CollectiveDetailsLoader({ booking }: { booking: BookingRow }) {
  const { data, isLoading } = useSWR(
    [GET_COLLECTIVE_BOOKING_BY_ID_QUERY_KEY, Number(booking.bookingId)],
    ([, idParam]) => api.getCollectiveBookingById(idParam)
  )

  if (isLoading || !data) {
    return (
      <div className={styles['loader']}>
        <Spinner />
      </div>
    )
  }

  return (
    <div className={styles['details-cell']}>
      <CollectiveBookingDetails bookingDetails={data} bookingRecap={booking} />
    </div>
  )
}

/**
 * Colonnes “Collectif” + (optionnel) full-row content.
 * -> Passez `bookings` pour alimenter l'entête “Statut” (filtre).
 */
export function useCollectiveBookingsColumns(
  opts: UseCollectiveBookingsColumnsOpts
) {
  const {
    bookings,
    bookingStatuses = [],
    updateGlobalFilters,
    expandedIds,
    onToggle,
  } = opts

  const columns: Column<BookingRow>[] = [
    {
      id: 'booking',
      label: 'Réservation',
      render: (row) => (
        <div className={styles['cell-item-wrapper']}>{row.bookingId}</div>
      ),
    },
    {
      id: 'offer',
      label: 'Nom de l’offre',
      sortable: true,
      ordererField: (row) => row.stock.offerName?.toLocaleLowerCase?.() ?? '',
      render: (row) => (
        <div
          className={cn(
            styles['cell-item-wrapper'],
            styles['offer-details-wrapper']
          )}
        >
          <BookingOfferCell booking={row} className={undefined} />
        </div>
      ),
    },
    {
      id: 'institution',
      label: 'Établissement',
      sortable: true,
      ordererField: sortInstitution,
      render: (row) => (
        <div className={styles['cell-item-wrapper']}>
          <div>
            <span data-testid="booking-offer-institution">
              {institutionName(row)}
            </span>
            <br />
          </div>
          <span className={styles['institution-cell-subtitle']}>
            {institutionAddress(row)}
          </span>
        </div>
      ),
    },
    {
      id: 'placesAndPrice',
      label: 'Places et prix',
      render: (row) => {
        const qty = row.stock.numberOfTickets
        return (
          <div className={styles['cell-item-wrapper']}>
            <div>
              {qty} {pluralizeString('place', qty)}
            </div>
            <div>
              {formatPrice(row.bookingAmount, {
                minimumFractionDigits: 2,
                maximumFractionDigits: 2,
                trailingZeroDisplay: 'stripIfInteger',
              })}
            </div>
          </div>
        )
      },
    },
    {
      id: 'status',
      // label pour a11y / data-label mobile
      label: 'Statut',
      // ✅ composant en-tête si on a le callback de filtres + la liste
      header: updateGlobalFilters ? (
        <FilterByBookingStatus
          bookingsRecap={bookings}
          updateGlobalFilters={updateGlobalFilters}
          audience={Audience.COLLECTIVE}
          bookingStatuses={bookingStatuses}
        />
      ) : undefined,
      render: (row) => (
        <CollectiveBookingStatusCell
          booking={row}
          className={styles['cell-item-wrapper']}
        />
      ),
    },
    {
      id: 'details',
      label: 'Détails',
      render: (row) => (
        <DetailsButtonCell
          controlledId={`booking-details-${row.bookingId}`}
          isExpanded={expandedIds?.has(row.id) ?? false}
          className={styles['cell-item-wrapper']}
          onClick={() => onToggle?.(row.id)}
        />
      ),
    },
  ]

  const detailsRef = useRef<HTMLTableRowElement | null>(null)

  // Ligne de détails plein-largeur (optionnelle)
  const getFullRowContentCollective = (row: BookingRow) => {
    if (expandedIds?.has(row.id)) {
      setTimeout(
        () =>
          detailsRef.current?.scrollIntoView({
            behavior: doesUserPreferReducedMotion() ? 'auto' : 'smooth',
          }),
        100
      )
    }
    return expandedIds?.has(row.id) ? (
      <div ref={detailsRef} className={styles['table-fullrow-content']}>
        <CollectiveDetailsLoader booking={row} />
      </div>
    ) : null
  }

  return { columns, getFullRowContentCollective }
}
