import cn from 'classnames'
import { format } from 'date-fns'

import {
  convertEuroToPacificFranc,
  formatPacificFranc,
} from '@/commons/utils/convertEuroToPacificFranc'
import { FORMAT_DD_MM_YYYY } from '@/commons/utils/date'
import { formatPrice } from '@/commons/utils/formatPrice'
import { pluralizeFr } from '@/commons/utils/pluralize'
import { DetailedModal } from '@/design-system/DetailedModal/DetailedModal'
import {
  InvoiceActions,
  InvoiceActionVariant,
} from '@/pages/Reimbursements/ReimbursementsInvoices/InvoiceTable/InvoiceActions'
import { Divider } from '@/ui-kit/Divider/Divider'

import type { ExtendedSettlementResponseModel } from '../SettlementTable/SettlementTable'
import styles from './SettlementRowInvoicesModal.module.scss'

type SettlementRowInvoicesModalProps = {
  isOpen: boolean
  onClose: () => void
  settlementRow: ExtendedSettlementResponseModel | null
}

export const SettlementRowInvoicesModal = ({
  isOpen,
  onClose,
  settlementRow,
}: Readonly<SettlementRowInvoicesModalProps>): JSX.Element | null => {
  if (!settlementRow) {
    return null
  }

  let description = `${settlementRow.invoicesCount} ${pluralizeFr(settlementRow.invoicesCount, 'justificatif', 'justificatifs')} - `

  description += settlementRow.isCaledonian
    ? formatPacificFranc(convertEuroToPacificFranc(settlementRow.amount))
    : formatPrice(settlementRow.amount)

  return (
    <DetailedModal
      isOpen={isOpen}
      onClose={onClose}
      title={settlementRow.label}
    >
      <div className={styles['modal-content']}>
        <p className={styles['modal-content-description']}>{description}</p>
        {settlementRow.invoices.map((invoice) => (
          <div key={invoice.reference}>
            <Divider />
            <div className={styles['modal-content-invoice-info']}>
              <p>
                {invoice.reference}
                <br />
                <span className={styles['invoice-date']}>
                  {format(new Date(invoice.date), FORMAT_DD_MM_YYYY)}
                </span>
              </p>
              <p
                className={cn({
                  [styles['negative-amount']]: invoice.amount < 0,
                  [styles['positive-amount']]: invoice.amount > 0,
                })}
              >
                {settlementRow.isCaledonian
                  ? formatPacificFranc(
                      convertEuroToPacificFranc(invoice.amount),
                      {
                        signDisplay: 'always',
                      }
                    )
                  : formatPrice(invoice.amount, { signDisplay: 'always' })}
              </p>
            </div>
            <div className={styles['invoice-actions']}>
              <InvoiceActions
                invoice={invoice}
                variant={InvoiceActionVariant.BUTTONS}
              />
            </div>
          </div>
        ))}
      </div>
    </DetailedModal>
  )
}
