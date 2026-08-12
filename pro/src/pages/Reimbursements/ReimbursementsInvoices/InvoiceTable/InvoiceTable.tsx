import cn from 'classnames'
import { format } from 'date-fns'
import { useState } from 'react'

import type { InvoiceResponseV2Model } from '@/apiClient/v1'
import {
  convertEuroToPacificFranc,
  formatPacificFranc,
} from '@/commons/utils/convertEuroToPacificFranc'
import { FORMAT_DD_MM_YYYY } from '@/commons/utils/date'
import { formatPrice } from '@/commons/utils/formatPrice'
import strokeRepaymentIcon from '@/icons/stroke-repayment.svg'
import { type Column, Table, TableVariant } from '@/ui-kit/Table/Table'

import { InvoiceActions } from './InvoiceActions'
import { InvoiceDownloadActionsButton } from './InvoiceDownloadActionsButton'
import styles from './InvoiceTable.module.scss'

const columns: Column<ExtendedInvoiceResponseV2Model>[] = [
  {
    id: 'reference',
    label: 'Référence',
    sortable: true,
    ordererField: 'reference',
    render: (invoice) => invoice.reference,
  },
  {
    id: 'documentType',
    label: 'Type de document',
    sortable: true,
    ordererField: 'amount',
    render: (invoice) =>
      invoice.amount >= 0 ? (
        <span className={styles['cell-document-type']}>Remboursement</span>
      ) : (
        <span className={styles['cell-document-type']}>Trop&nbsp;perçu</span>
      ),
  },
  {
    id: 'date',
    label: "Date d'émission",
    sortable: true,
    ordererField: 'date',
    render: (invoice) => format(new Date(invoice.date), FORMAT_DD_MM_YYYY),
  },
  {
    id: 'amount',
    label: 'Montant',
    render: (invoice: ExtendedInvoiceResponseV2Model) => (
      <div
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
      </div>
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
    header: <div className={styles['cell-actions']}>Actions</div>,
  },
]

type InvoiceTableProps = {
  data: InvoiceResponseV2Model[]
  hasInvoice: boolean
  isLoading: boolean
  isCaledonian?: boolean
  onFilterReset: () => void
}

type ExtendedInvoiceResponseV2Model = InvoiceResponseV2Model & {
  id: string
  isCaledonian?: boolean
}

export const InvoiceTable = ({
  data,
  hasInvoice,
  isLoading,
  isCaledonian,
  onFilterReset,
}: InvoiceTableProps) => {
  const [checkedInvoices, setCheckedInvoices] = useState<string[]>([])

  const getInvoiceDateLabel = (invoice: ExtendedInvoiceResponseV2Model) =>
    format(new Date(invoice.date), FORMAT_DD_MM_YYYY)

  const invoices: ExtendedInvoiceResponseV2Model[] = hasInvoice
    ? data.map((invoice) => ({
        ...invoice,
        id: invoice.reference,
        isCaledonian: isCaledonian,
      }))
    : []

  return (
    <div className={styles['invoices-table']}>
      <InvoiceDownloadActionsButton checkedInvoices={checkedInvoices} />
      <Table
        title="Justificatif de remboursement ou de trop perçu"
        columns={columns}
        data={invoices}
        selectable={true}
        getRowSelectionDateTime={getInvoiceDateLabel}
        isLoading={isLoading}
        onSelectionChange={(rows) => {
          setCheckedInvoices(rows.map((row) => row.reference.toString()))
        }}
        variant={TableVariant.COLLAPSE}
        noResult={{
          message:
            'Aucun justificatif de remboursement trouvé pour votre recherche',
          onFilterReset,
        }}
        noData={{
          hasNoData: !hasInvoice,
          message: {
            icon: strokeRepaymentIcon,
            title:
              'Vous n’avez pas encore de justificatifs de remboursement disponibles',
            subtitle:
              'Lorsqu’ils auront été édités, vous pourrez les télécharger ici',
          },
        }}
      />
    </div>
  )
}
