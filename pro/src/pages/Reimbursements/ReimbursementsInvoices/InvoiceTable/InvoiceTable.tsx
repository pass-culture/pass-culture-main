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
import { Button } from '@/design-system/Button/Button'
import {
  ButtonColor,
  ButtonVariant,
  IconPositionEnum,
} from '@/design-system/Button/types'
import fullNextIcon from '@/icons/full-next.svg'
import strokeInstitutionIcon from '@/icons/stroke-institution.svg'
import strokeRepaymentIcon from '@/icons/stroke-repayment.svg'
import { type Column, Table, TableVariant } from '@/ui-kit/Table/Table'

import { InvoiceActions } from './InvoiceActions'
import { InvoiceDownloadActionsBar } from './InvoiceDownloadActionsBar'
import styles from './InvoiceTable.module.scss'

function getEmptyStateMessage(hasBankAccount: boolean) {
  if (!hasBankAccount) {
    return {
      icon: strokeInstitutionIcon,
      title: 'Aucun compte bancaire rattaché',
      subtitle:
        "Vos justificatifs ne pourront pas être traités tant qu'aucun compte bancaire n'est actif. Rattachez-en un pour débloquer vos remboursements.",
      cta: (
        <Button
          as="router-link"
          to="/administration/remboursements/informations-bancaires"
          label="Rattacher un compte bancaire"
          variant={ButtonVariant.TERTIARY}
          color={ButtonColor.NEUTRAL}
          icon={fullNextIcon}
          iconPosition={IconPositionEnum.RIGHT}
        />
      ),
    }
  }
  return {
    icon: strokeRepaymentIcon,
    title: 'Aucun justificatif pour le moment',
    subtitle:
      'Les justificatifs sont générés à partir de vos réservations validées. Ils apparaîtront ici automatiquement.',
    cta: (
      <Button
        as="a"
        to="https://aide.passculture.app/hc/fr/articles/4411999149201--Acteurs-Culturels-Comment-effectuer-le-suivi-de-vos-remboursements"
        opensInNewTab
        label="Comprendre le suivi des remboursements"
        variant={ButtonVariant.TERTIARY}
        color={ButtonColor.NEUTRAL}
        iconPosition={IconPositionEnum.RIGHT}
      />
    ),
  }
}

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
    label: 'Type de justificatif',
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
    sortable: true,
    ordererField: 'amount',
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
  hasBankAccount: boolean
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
  hasBankAccount,
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
          message: 'Aucun justificatif ne correspond à votre recherche',
          subtitle: 'Essayez de modifier vos critères de recherche.',
          resetMessage: 'Réinitialiser les filtres',
          onFilterReset,
        }}
        noData={{
          hasNoData: !hasInvoice || !hasBankAccount,
          message: getEmptyStateMessage(hasBankAccount),
        }}
      >
        <InvoiceDownloadActionsBar checkedInvoices={checkedInvoices} />
      </Table>
    </div>
  )
}
