import cn from 'classnames'

import type { BookingRecapResponseModel } from '@/apiClient/v1'
import { Audience, type CurrencyCode } from '@/commons/core/shared/types'
import { useIsCaledonian } from '@/commons/hooks/useIsCaledonian'
import { convertPrice } from '@/commons/utils/convertPrice'
import { formatPrice } from '@/commons/utils/formatPrice'
import strokeDuoIcon from '@/icons/stroke-duo.svg'
import { SvgIcon } from '@/ui-kit/SvgIcon/SvgIcon'
import type { Column } from '@/ui-kit/Table/Table'

import { FilterByBookingStatus } from '../Components/Filters/FilterByBookingStatus'
import type { BookingsFilters } from '../Components/types'
import { BeneficiaryCell } from './Cells/BeneficiaryCell'
import { BookingDateCell } from './Cells/BookingDateCell'
import { BookingOfferCell } from './Cells/BookingOfferCell'
import { BookingStatusCell } from './Cells/BookingStatusCell'
import { BookingStatusCellHistory } from './Cells/BookingStatusCellHistory'
import { DetailsButtonCell } from './Cells/DetailsButtonCell'
import styles from './IndividualBookingsTable.module.scss'

type BookingRow = BookingRecapResponseModel & { id: number }
const priceText = (amount: number, currency: CurrencyCode) => {
  if (!amount) return 'Gratuit'
  return formatPrice(convertPrice(amount, { to: currency }), { currency })
}

type Opts = {
  bookings: BookingRecapResponseModel[]
  bookingStatuses?: string[]
  updateGlobalFilters?: (updated: Partial<BookingsFilters>) => void
  expandedIds?: Set<string | number>
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
  const currency: CurrencyCode = isCaledonian ? 'XPF' : 'EUR'

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
      label: 'Statut',
      header: updateGlobalFilters ? (
        <FilterByBookingStatus
          bookingStatuses={bookingStatuses}
          bookingsRecap={bookings}
          updateGlobalFilters={updateGlobalFilters}
          audience={Audience.INDIVIDUAL}
        />
      ) : undefined,
      render: (row) => (
        <BookingStatusCell
          booking={row}
          className={styles['cell-item-wrapper']}
        />
      ),
    },
    {
      id: 'details',
      label: '',
      render: (row) => (
        <DetailsButtonCell
          controlledId={`booking-details-${row.id}`}
          isExpanded={expandedIds?.has(row.id) ?? false}
          className={styles['cell-item-wrapper']}
          onClick={() => onToggle?.(row.id)}
        />
      ),
    },
  ]

  const getFullRowContentIndividual = (row: BookingRow) => {
    if (!expandedIds?.has(row.id)) {
      return null
    }
    return (
      <div className={styles['table-fullrow-content']}>
        <div>
          <span className={styles['details-title']}>Prix : </span>
          <span className={styles['details-content']}>
            {priceText(row.bookingAmount, currency)}
          </span>
        </div>
        <BookingStatusCellHistory
          index={row.id}
          bookingStatusHistory={row.bookingStatusHistory}
        />
      </div>
    )
  }

  return { columns, getFullRowContentIndividual }
}
