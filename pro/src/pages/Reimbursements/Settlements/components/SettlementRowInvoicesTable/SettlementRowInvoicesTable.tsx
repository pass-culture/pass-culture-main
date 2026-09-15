import cn from 'classnames'
import { format } from 'date-fns'

import type { InvoiceResponseV2Model } from '@/apiClient/v1'
import { useAppSelector } from '@/commons/hooks/useAppSelector'
import { ensureSelectedAdminOfferer } from '@/commons/store/user/selectors'
import {
  convertEuroToPacificFranc,
  formatPacificFranc,
} from '@/commons/utils/convertEuroToPacificFranc'
import { FORMAT_DD_MM_YYYY } from '@/commons/utils/date'
import { formatPrice } from '@/commons/utils/formatPrice'
import { noop } from '@/commons/utils/noop'
import strokeRepaymentIcon from '@/icons/stroke-repayment.svg'
import { InvoiceActions } from '@/pages/Reimbursements/ReimbursementsInvoices/InvoiceTable/InvoiceActions'
import { Table, TableVariant } from '@/ui-kit/Table/Table'

import styles from './SettlementRowInvoicesTable.module.scss'

type SettlementRowInvoicesTableProps = {
  invoices: InvoiceResponseV2Model[]
}

type ExtendedInvoiceResponseV2Model = InvoiceResponseV2Model & {
  id: string
  isCaledonian?: boolean
}

const columns = [
  {
    id: 'reference',
    label: 'Référence',
    header: <p className={styles['cell-reference-header']}>Référence</p>,
    render: (invoice: ExtendedInvoiceResponseV2Model) => (
      <p className={styles['cell-reference']}>{invoice.reference}</p>
    ),
  },
  {
    id: 'date',
    label: "Date d'émission",
    render: (invoice: ExtendedInvoiceResponseV2Model) => (
      <p>{format(new Date(invoice.date), FORMAT_DD_MM_YYYY)}</p>
    ),
  },
  {
    id: 'amount',
    label: 'Montant',
    render: (invoice: ExtendedInvoiceResponseV2Model) => (
      <p
        className={cn({
          [styles['negative-amount']]: invoice.amount < 0,
          [styles['positive-amount']]: invoice.amount > 0,
        })}
      >
        {invoice.isCaledonian
          ? formatPacificFranc(convertEuroToPacificFranc(invoice.amount), {
              signDisplay: 'always',
            })
          : formatPrice(invoice.amount, { signDisplay: 'always' })}
      </p>
    ),
  },
  {
    id: 'actions',
    label: 'Actions',
    render: (invoice: ExtendedInvoiceResponseV2Model) => (
      <div className={styles['cell-actions']}>
        <InvoiceActions invoice={invoice} />
      </div>
    ),
    header: <p className={styles['cell-actions-header']}>Actions</p>,
  },
]

export const SettlementRowInvoicesTable = ({
  invoices,
}: Readonly<SettlementRowInvoicesTableProps>): JSX.Element => {
  const selectedAdminOfferer = useAppSelector(ensureSelectedAdminOfferer)

  return (
    <Table
      data={invoices.map((i) => ({
        ...i,
        id: i.reference,
        isCaledonian: selectedAdminOfferer.isCaledonian,
      }))}
      className={styles['settlement-row-invoice-table']}
      columns={columns}
      isLoading={false}
      variant={TableVariant.COLLAPSE}
      noResult={{
        message: 'Aucun justificatif ne correspond à votre recherche',
        subtitle: 'Essayez de modifier vos critères de recherche.',
        resetMessage: 'Réinitialiser les filtres',
        onFilterReset: noop,
      }}
      noData={{
        hasNoData: invoices.length === 0,
        message: {
          icon: strokeRepaymentIcon,
          title: 'Pas de justificatifs pour ce virement',
        },
      }}
    />
  )
}
