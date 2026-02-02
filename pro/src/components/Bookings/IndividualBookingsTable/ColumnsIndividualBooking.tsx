import type { BookingRecapResponseModel } from '@/apiClient/v1'
import { useIsCaledonian } from '@/commons/hooks/useIsCaledonian'
import {
  convertEuroToPacificFranc,
  formatPacificFranc,
} from '@/commons/utils/convertEuroToPacificFranc'
import { formatPrice } from '@/commons/utils/formatPrice'
import type { Column } from '@/ui-kit/Table/Table'

import { FilterByBookingStatus } from '../Components/Filters/FilterByBookingStatus'
import type { BookingsFilters } from '../Components/types'
import { BeneficiaryCell } from './Cells/BeneficiaryCell'
import { BookingDateCell } from './Cells/BookingDateCell'
import { BookingOfferCell } from './Cells/BookingOfferCell'
import { BookingStatusCell } from './Cells/BookingStatusCell'
import { BookingStatusCellHistory } from './Cells/BookingStatusCellHistory'
import { DetailsButtonCell } from './Cells/DetailsButtonCell'

type BookingRow = BookingRecapResponseModel & { id: number }
const priceText = (amount: number) => (amount ? formatPrice(amount) : 'Gratuit')

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

  const columns: Column<BookingRow>[] = [
    {
      id: 'offer',
      label: 'Nom de l’offre',
      sortable: true,
      ordererField: (row) => row.stock.offerName,
      render: (row) => (
        <BookingOfferCell booking={row} isCaledonian={isCaledonian} />
      ),
    },
    {
      id: 'beneficiary',
      label: 'Bénéficiaire',
      sortable: true,
      ordererField: (row) => row.beneficiary.firstname,
      render: (row) => <BeneficiaryCell beneficiaryInfos={row.beneficiary} />,
    },
    {
      id: 'bookingDate',
      label: 'Réservation',
      sortable: true,
      ordererField: (row) => new Date(row.bookingDate).getTime(),
      render: (row) => (
        <BookingDateCell bookingDateTimeIsoString={row.bookingDate} />
      ),
    },
    {
      id: 'bookingToken',
      label: 'Contremarque',
      sortable: true,
      ordererField: (row) => row.bookingToken ?? '',
      render: (row) => <span>{row.bookingToken || '-'}</span>,
    },
    {
      id: 'status',
      label: 'Statut',
      header: updateGlobalFilters ? (
        <FilterByBookingStatus
          bookingStatuses={bookingStatuses}
          bookingsRecap={bookings}
          updateGlobalFilters={updateGlobalFilters}
        />
      ) : undefined,
      render: (row) => <BookingStatusCell booking={row} />,
    },
    {
      id: 'details',
      label: '',
      render: (row) => (
        <DetailsButtonCell
          controlledId={`booking-details-${row.id}`}
          isExpanded={expandedIds?.has(row.id) ?? false}
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
      <>
        <div>
          <span>Prix : </span>
          <span>
            {isCaledonian
              ? formatPacificFranc(convertEuroToPacificFranc(row.bookingAmount))
              : priceText(row.bookingAmount)}
          </span>
        </div>
        <BookingStatusCellHistory
          index={row.id}
          bookingStatusHistory={row.bookingStatusHistory}
        />
      </>
    )
  }

  return { columns, getFullRowContentIndividual }
}
