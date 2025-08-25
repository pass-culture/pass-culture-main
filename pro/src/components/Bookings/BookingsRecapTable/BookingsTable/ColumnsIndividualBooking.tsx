import cn from 'classnames'

import type { BookingRecapResponseModel } from '@/apiClient/v1'
import { Audience } from '@/commons/core/shared/types'
import { useIsCaledonian } from '@/commons/hooks/useIsCaledonian'
import {
  convertEuroToPacificFranc,
  formatPacificFranc,
} from '@/commons/utils/convertEuroToPacificFranc'
import { formatPrice } from '@/commons/utils/formatPrice'
import strokeDuoIcon from '@/icons/stroke-duo.svg'
import { SvgIcon } from '@/ui-kit/SvgIcon/SvgIcon'
import type { Column } from '@/ui-kit/Table/Table'

import { FilterByBookingStatus } from '../Filters/FilterByBookingStatus'
import type { BookingsFilters } from '../types'
import styles from './BookingsTable.module.scss'
import { BeneficiaryCell } from './Cells/BeneficiaryCell'
import { BookingDateCell } from './Cells/BookingDateCell'
import { BookingOfferCell } from './Cells/BookingOfferCell'
import { BookingStatusCellHistory } from './Cells/BookingStatusCellHistory'
import { DetailsButtonCell } from './Cells/DetailsButtonCell'
import { IndividualBookingStatusCell } from './Cells/IndividualBookingStatusCell'

type BookingRow = BookingRecapResponseModel & { id: number }
const priceText = (amount: number) => (amount ? formatPrice(amount) : 'Gratuit')

type Opts = {
  /** liste complète pour alimenter l’entête du filtre */
  bookings: BookingRecapResponseModel[]
  /** statuts disponibles pour le filtre */
  bookingStatuses?: string[]
  /** callback global pour MAJ des filtres */
  updateGlobalFilters?: (updated: Partial<BookingsFilters>) => void

  /** gestion du détail (ligne fullrow) */
  expandedIds?: number | Set<string | number>
  onToggle?: (id: string | number) => void
}

export function useBookingsTableColumnsByIndex(opts: Opts) {
  const {
    bookings,
    bookingStatuses = [],
    updateGlobalFilters,
    expandedIds,
    onToggle,
  } = opts

  const isCaledonian = useIsCaledonian()

  const columns: Column<BookingRow>[] = [
    {
      id: 'offer',
      label: 'Nom de l’offre',
      sortable: true,
      ordererField: (row) => row.stock.offerName,
      render: (row) => (
        <div
          className={cn(
            styles['cell-item-wrapper'],
            styles['offer-details-wrapper']
          )}
        >
          <BookingOfferCell booking={row} isCaledonian={isCaledonian} />
          {row.bookingIsDuo && (
            <SvgIcon
              src={strokeDuoIcon}
              alt="Réservation DUO"
              className={styles['bookings-duo-icon']}
            />
          )}
        </div>
      ),
    },
    {
      id: 'beneficiary',
      label: 'Bénéficiaire',
      sortable: true,
      ordererField: (row) => row.beneficiary.firstname,
      render: (row) => (
        <BeneficiaryCell
          beneficiaryInfos={row.beneficiary}
          className={styles['cell-item-wrapper']}
        />
      ),
    },
    {
      id: 'bookingDate',
      label: 'Réservation',
      sortable: true,
      ordererField: (row) => new Date(row.bookingDate).getTime(),
      render: (row) => (
        <BookingDateCell
          bookingDateTimeIsoString={row.bookingDate}
          className={styles['cell-item-wrapper']}
        />
      ),
    },
    {
      id: 'bookingToken',
      label: 'Contremarque',
      sortable: true,
      ordererField: (row) => row.bookingToken ?? '',
      render: (row) => (
        <span className={styles['cell-item-wrapper']}>
          {row.bookingToken || '-'}
        </span>
      ),
    },
    {
      id: 'status',
      // libellé pour a11y / data-label mobile
      label: 'Statut',
      // 🧩 composant de filtre directement dans l’entête
      header: updateGlobalFilters ? (
        <FilterByBookingStatus
          bookingStatuses={bookingStatuses}
          bookingsRecap={bookings}
          updateGlobalFilters={updateGlobalFilters}
          audience={Audience.INDIVIDUAL}
        />
      ) : undefined,
      render: (row) => (
        <IndividualBookingStatusCell
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
          controlledId={`booking-details-${row.id}`} // 🧩 use index
          isExpanded={opts.expandedIds?.has(row.id) ?? false}
          className={styles['cell-item-wrapper']}
          onClick={() => opts.onToggle?.(row.id)} // 🧩 toggle by index
        />
      ),
    },
  ]

  const getFullRowContentIndividual = (row: BookingRow) => {
    if (!opts.expandedIds?.has(row.id)) return null
    return (
      <div className={styles['table-fullrow-content']}>
        <div>
          <span className={styles['details-title']}>Prix : </span>
          <span className={styles['details-content']}>
            {isCaledonian
              ? formatPacificFranc(convertEuroToPacificFranc(row.bookingAmount))
              : priceText(row.bookingAmount)}
          </span>
        </div>
        <BookingStatusCellHistory
          index={row.id} // 🧩 pass index
          bookingStatusHistory={row.bookingStatusHistory}
        />
      </div>
    )
  }

  return { columns, getFullRowContentIndividual }
}
