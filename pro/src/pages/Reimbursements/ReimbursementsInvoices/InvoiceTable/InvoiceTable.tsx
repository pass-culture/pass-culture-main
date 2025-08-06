import cn from 'classnames'
import { format } from 'date-fns'
import { useState } from 'react'

import { InvoiceResponseV2Model } from '@/apiClient//v1'
import { FORMAT_DD_MM_YYYY } from '@/commons/utils/date'
import { formatPrice } from '@/commons/utils/formatPrice'
import strokeLessIcon from '@/icons/stroke-less.svg'
import strokeMoreIcon from '@/icons/stroke-more.svg'
import strokeRepaymentIcon from '@/icons/stroke-repayment.svg'
import { SvgIcon } from '@/ui-kit/SvgIcon/SvgIcon'
import { Column, Table, TableVariant } from '@/ui-kit/Table/Table'

import { InvoiceActions } from './InvoiceActions'
import { InvoiceDownloadActionsButton } from './InvoiceDownloadActionsButton'
import styles from './InvoiceTable.module.scss'

const columns: Column<InvoiceResponseV2Model>[] = [
  {
    id: 'date',
    label: 'Date du justificatif',
    sortable: true,
    ordererField: 'date',
    render: (invoice) => format(new Date(invoice.date), FORMAT_DD_MM_YYYY),
  },
  {
    id: 'documentType',
    label: 'Type de document',
    sortable: true,
    ordererField: 'amount',
    render: (invoice) =>
      invoice.amount >= 0 ? (
        <span className={styles['cell-document-type']}>
          <SvgIcon
            src={strokeMoreIcon}
            alt=""
            className={styles['more-icon']}
            width="16"
          />
          Remboursement
        </span>
      ) : (
        <span className={styles['cell-document-type']}>
          <SvgIcon
            src={strokeLessIcon}
            alt=""
            className={styles['less-icon']}
            width="16"
          />
          Trop&nbsp;perçu
        </span>
      ),
  },
  {
    id: 'bankAccountLabel',
    label: 'Point de remboursement',
    sortable: true,
    ordererField: 'bankAccountLabel',
    render: (invoice: InvoiceResponseV2Model) => (
      <div className={styles['cell-bank-account']}>
        {invoice.bankAccountLabel}
      </div>
    ),
  },
  {
    id: 'cashflowLabel',
    label: 'N° de virement',
    sortable: true,
    ordererField: 'cashflowLabels',
    render: (invoice: InvoiceResponseV2Model) =>
      invoice.amount >= 0 ? invoice.cashflowLabels[0] : 'N/A',
  },
  {
    id: 'amount',
    label: 'Montant remboursé',
    render: (invoice: InvoiceResponseV2Model) => (
      <div
        className={cn(styles['cell-amount'], {
          [styles['negative-amount']]: invoice.amount < 0,
        })}
      >
        {formatPrice(invoice.amount, {
          signDisplay: 'always',
        })}
      </div>
    ),
  },
  {
    id: 'actions',
    label: 'Actions',
    render: (invoice: InvoiceResponseV2Model) => (
      <div className={styles['cell-actions']}>
        <InvoiceActions invoice={invoice} />
      </div>
    ),
  },
]

type InvoiceTableProps = {
  data: InvoiceResponseV2Model[]
  hasInvoice: boolean
  isLoading: boolean
  onFilterReset: () => void
}

export const InvoiceTable = ({
  data,
  hasInvoice,
  isLoading,
  onFilterReset,
}: InvoiceTableProps) => {
  const [checkedInvoices, setCheckedInvoices] = useState<string[]>([])

  const invoices = hasInvoice
    ? data.map((invoice) => ({
        ...invoice,
        id: invoice.reference,
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
