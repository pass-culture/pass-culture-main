import cn from 'classnames'
import { compareAsc, format } from 'date-fns'

import { InvoiceResponseV2Model } from 'apiClient/v1'
import { SortArrow } from 'components/StocksEventList/SortArrow'
import {
  SortingMode,
  giveSortingModeForAlly,
  useColumnSorting,
} from 'hooks/useColumnSorting'
import strokeLessIcon from 'icons/stroke-less.svg'
import strokeMoreIcon from 'icons/stroke-more.svg'
import { SvgIcon } from 'ui-kit/SvgIcon/SvgIcon'
import { FORMAT_DD_MM_YYYY } from 'utils/date'
import { formatPrice } from 'utils/formatPrice'

import { InvoiceActions } from './InvoiceActions'
import styles from './InvoiceTable.module.scss'

type InvoiceTableProps = {
  invoices: InvoiceResponseV2Model[]
}

enum InvoicesOrderedBy {
  DATE = 'date',
  REIMBURSEMENT_POINT_NAME = 'reimbursementPointName',
  REFERENCE = 'reference',
  CASHFLOW_LABELS = 'cashflowLabels',
  DOCUMENT_TYPE = 'documentType',
}

function sortInvoices(
  invoices: InvoiceResponseV2Model[],
  currentSortingColumn: InvoicesOrderedBy | null,
  sortingMode: SortingMode
) {
  if (sortingMode === SortingMode.NONE) {
    return invoices
  }
  switch (currentSortingColumn) {
    case InvoicesOrderedBy.DATE:
      return [...invoices].sort((a, b) =>
        sortingMode === SortingMode.ASC
          ? compareAsc(new Date(a.date), new Date(b.date))
          : compareAsc(new Date(b.date), new Date(a.date))
      )

    // TODO : remove me when removing WIP_ENABLE_FINANCE_INCIDENT
    case InvoicesOrderedBy.REIMBURSEMENT_POINT_NAME:
      return [...invoices].sort((a, b) =>
        sortingMode === SortingMode.ASC
          ? (a.bankAccountLabel ?? '').localeCompare(b.bankAccountLabel ?? '')
          : (b.bankAccountLabel ?? '').localeCompare(a.bankAccountLabel ?? '')
      )

    case InvoicesOrderedBy.DOCUMENT_TYPE:
      return [...invoices].sort((a, b) => {
        // document type is juste assumed from amount :
        // 1 for positive amount, -1 for negative amount
        const documentTypeA = a.amount >= 0 ? 1 : -1
        const documentTypeB = b.amount >= 0 ? 1 : -1

        return sortingMode === SortingMode.ASC
          ? documentTypeA - documentTypeB
          : documentTypeB - documentTypeA
      })

    case InvoicesOrderedBy.REFERENCE:
      return [...invoices].sort((a, b) =>
        sortingMode === SortingMode.ASC
          ? a.reference.localeCompare(b.reference)
          : b.reference.localeCompare(a.reference)
      )

    case InvoicesOrderedBy.CASHFLOW_LABELS:
      return [...invoices].sort((a, b) =>
        sortingMode === SortingMode.ASC
          ? a.cashflowLabels[0].localeCompare(b.cashflowLabels[0])
          : b.cashflowLabels[0].localeCompare(a.cashflowLabels[0])
      )

    default:
      return invoices
  }
}

export const InvoiceTable = ({ invoices }: InvoiceTableProps) => {
  const { currentSortingColumn, currentSortingMode, onColumnHeaderClick } =
    useColumnSorting<InvoicesOrderedBy>()

  const sortedInvoices = sortInvoices(
    invoices,
    currentSortingColumn,
    currentSortingMode
  )

  return (
    <table role="table" className={styles['invoices-table']}>
      <caption className="visually-hidden">
        Justificatif de remboursement ou de trop perçu
      </caption>
      <thead className={styles['header']}>
        <tr role="row">
          <th
            role="columnheader"
            scope="col"
            className={cn(styles['header-cell'], styles['date-column'])}
          >
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
            >
              {currentSortingColumn === InvoicesOrderedBy.DATE && (
                <span className="visually-hidden">
                  Tri par date {giveSortingModeForAlly(currentSortingMode)}{' '}
                  activé.
                </span>
              )}
            </SortArrow>
          </th>

          <th
            role="columnheader"
            scope="col"
            className={cn(
              styles['header-cell'],
              styles['document-type-column']
            )}
          >
            Type de document
            <SortArrow
              sortingMode={
                currentSortingColumn === InvoicesOrderedBy.DOCUMENT_TYPE
                  ? currentSortingMode
                  : SortingMode.NONE
              }
              onClick={() => {
                onColumnHeaderClick(InvoicesOrderedBy.DOCUMENT_TYPE)
              }}
            >
              {currentSortingColumn === InvoicesOrderedBy.DOCUMENT_TYPE && (
                <span className="visually-hidden">
                  Tri par type de document{' '}
                  {giveSortingModeForAlly(currentSortingMode)} activé.
                </span>
              )}
            </SortArrow>
          </th>
          <th
            role="columnheader"
            scope="col"
            className={cn(styles['header-cell'], styles['bank-account-column'])}
          >
            Compte bancaire
            <SortArrow
              sortingMode={
                currentSortingColumn ===
                InvoicesOrderedBy.REIMBURSEMENT_POINT_NAME
                  ? currentSortingMode
                  : SortingMode.NONE
              }
              onClick={() => {
                onColumnHeaderClick(InvoicesOrderedBy.REIMBURSEMENT_POINT_NAME)
              }}
            >
              {currentSortingColumn ===
                InvoicesOrderedBy.REIMBURSEMENT_POINT_NAME && (
                <span className="visually-hidden">
                  Tri par compte bancaire
                  {giveSortingModeForAlly(currentSortingMode)} activé.
                </span>
              )}
            </SortArrow>
          </th>
          <th
            role="columnheader"
            scope="col"
            className={cn(styles['header-cell'], styles['label-column'])}
          >
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
            >
              {currentSortingColumn === InvoicesOrderedBy.CASHFLOW_LABELS && (
                <span className="visually-hidden">
                  Tri par n° de virement{' '}
                  {giveSortingModeForAlly(currentSortingMode)} activé.
                </span>
              )}
            </SortArrow>
          </th>
          <th
            role="columnheader"
            scope="col"
            className={cn(styles['header-cell'], styles['amount-column'])}
          >
            Montant remboursé
          </th>
        </tr>
      </thead>

      <tbody className={styles['body']}>
        {sortedInvoices.map((invoice) => {
          return (
            <tr role="row" key={invoice.reference} className={styles['row']}>
              <td
                role="cell"
                className={cn(
                  styles['data'],
                  styles['date-column'],
                  styles['date-data']
                )}
                data-label="Date du justificatif"
              >
                {format(new Date(invoice.date), FORMAT_DD_MM_YYYY)}
              </td>
              <td
                role="cell"
                className={cn(styles['data'], styles['document-type-column'])}
                data-label="Type de document"
              >
                {invoice.amount >= 0 ? (
                  <span className={styles['document-type-content']}>
                    <SvgIcon
                      src={strokeMoreIcon}
                      alt=""
                      className={styles['more-icon']}
                      width="16"
                    />
                    Remboursement
                  </span>
                ) : (
                  <span className={styles['document-type-content']}>
                    <SvgIcon
                      src={strokeLessIcon}
                      alt=""
                      className={styles['less-icon']}
                      width="16"
                    />
                    Trop&nbsp;perçu
                  </span>
                )}
              </td>
              <td
                role="cell"
                className={cn(styles['data'], styles['bank-account-column'])}
                data-label="Point de remboursement"
              >
                {invoice.bankAccountLabel}
              </td>
              {/* For now only one label is possible by invoice. */}
              <td
                role="cell"
                className={cn(styles['data'], styles['label-column'])}
                data-label="N° de virement"
              >
                {invoice.amount >= 0 ? invoice.cashflowLabels[0] : 'N/A'}
              </td>
              <td
                role="cell"
                className={cn(styles['data'], styles['amount-column'], {
                  [styles['negative-amount']]: invoice.amount < 0,
                })}
                data-label="Montant remboursé"
              >
                {formatPrice(invoice.amount, {
                  signDisplay: 'always',
                })}
              </td>
              <td
                role="cell"
                className={cn(
                  styles['data'],
                  styles['invoice-column'],
                  styles['invoice-data']
                )}
                data-label="Téléchargements"
              >
                <InvoiceActions invoice={invoice} />
              </td>
            </tr>
          )
        })}
      </tbody>
    </table>
  )
}
