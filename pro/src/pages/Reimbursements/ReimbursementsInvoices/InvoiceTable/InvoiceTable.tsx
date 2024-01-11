import { InvoiceResponseModel } from 'apiClient/v1'
import { SortArrow } from 'components/StocksEventList/SortArrow'
import useActiveFeature from 'hooks/useActiveFeature'
import { SortingMode, useColumnSorting } from 'hooks/useColumnSorting'
import fullDownloadIcon from 'icons/full-download.svg'
import { ButtonLink } from 'ui-kit'
import { ButtonVariant } from 'ui-kit/Button/types'
import { formatPrice } from 'utils/formatPrice'

import styles from './InvoiceTable.module.scss'

type InvoiceTableProps = {
  invoices: InvoiceResponseModel[]
}

enum InvoicesOrderedBy {
  DATE = 'date',
  REIMBURSEMENT_POINT_NAME = 'reimbursementPointName',
  REFERENCE = 'reference',
  CASHFLOW_LABELS = 'cashflowLabels',
}

const InvoiceTable = ({ invoices }: InvoiceTableProps) => {
  const isNewBankDetailsJourneyEnabled = useActiveFeature(
    'WIP_ENABLE_NEW_BANK_DETAILS_JOURNEY'
  )
  const { currentSortingColumn, currentSortingMode, onColumnHeaderClick } =
    useColumnSorting<InvoicesOrderedBy>()

  return (
    <>
      <table className={styles['reimbursement-table']}>
        <thead>
          <tr>
            <th>
              Date du justificatif
              <SortArrow
                sortingMode={
                  currentSortingColumn === InvoicesOrderedBy.DATE
                    ? currentSortingMode
                    : SortingMode.NONE
                }
                onClick={() => {
                  onColumnHeaderClick(InvoicesOrderedBy.DATE)
                }}
              />
            </th>
            <th>
              {isNewBankDetailsJourneyEnabled
                ? 'Compte bancaire'
                : 'Point de remboursement'}
              &nbsp;
              <SortArrow
                sortingMode={
                  currentSortingColumn ===
                  InvoicesOrderedBy.REIMBURSEMENT_POINT_NAME
                    ? currentSortingMode
                    : SortingMode.NONE
                }
                onClick={() => {
                  onColumnHeaderClick(
                    InvoicesOrderedBy.REIMBURSEMENT_POINT_NAME
                  )
                }}
              />
            </th>
            <th>
              N° du justificatif
              <SortArrow
                sortingMode={
                  currentSortingColumn === InvoicesOrderedBy.REFERENCE
                    ? currentSortingMode
                    : SortingMode.NONE
                }
                onClick={() => {
                  onColumnHeaderClick(InvoicesOrderedBy.REFERENCE)
                }}
              />
            </th>
            <th>
              N° de virement
              <SortArrow
                sortingMode={
                  currentSortingColumn === InvoicesOrderedBy.CASHFLOW_LABELS
                    ? currentSortingMode
                    : SortingMode.NONE
                }
                onClick={() => {
                  onColumnHeaderClick(InvoicesOrderedBy.CASHFLOW_LABELS)
                }}
              />
            </th>
            <th>Montant remboursé</th>
          </tr>
        </thead>
        <tbody className={styles['reimbursement-body']}>
          {invoices.map((invoice) => {
            return (
              <tr key={invoice.reference}>
                <td className={styles['date']}>{invoice.date}</td>
                <td className={styles['reimbursement-point']}>
                  {invoice.reimbursementPointName}
                </td>
                <td className={styles['reference']}>{invoice.reference}</td>
                {/* For now only one label is possible by invoice. */}
                <td className={styles['label']}>{invoice.cashflowLabels[0]}</td>
                <td className={styles['amount']}>
                  {formatPrice(invoice.amount)}
                </td>
                <td className={styles['invoice']}>
                  <ButtonLink
                    link={{
                      isExternal: true,
                      to: invoice.url,
                      rel: 'noopener noreferrer',
                      target: '_blank',
                      'aria-label': 'Télécharger le PDF',
                      download: true,
                    }}
                    icon={fullDownloadIcon}
                    variant={ButtonVariant.TERNARY}
                  >
                    PDF
                  </ButtonLink>
                </td>
              </tr>
            )
          })}
        </tbody>
      </table>
    </>
  )
}

export default InvoiceTable
