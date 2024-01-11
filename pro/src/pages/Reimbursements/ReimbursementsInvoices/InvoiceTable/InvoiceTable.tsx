import cn from 'classnames'
import { format } from 'date-fns'

import { InvoiceResponseModel } from 'apiClient/v1'
import { SortArrow } from 'components/StocksEventList/SortArrow'
import useActiveFeature from 'hooks/useActiveFeature'
import { SortingMode, useColumnSorting } from 'hooks/useColumnSorting'
import fullDownloadIcon from 'icons/full-download.svg'
import strokeLessIcon from 'icons/stroke-less.svg'
import strokeMoreIcon from 'icons/stroke-more.svg'
import { ButtonLink } from 'ui-kit'
import { ButtonVariant } from 'ui-kit/Button/types'
import { SvgIcon } from 'ui-kit/SvgIcon/SvgIcon'
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
  DOCUMENT_TYPE = 'documentType',
}

function sortByDate(
  invoiceA: InvoiceResponseModel,
  invoiceB: InvoiceResponseModel
) {
  const invoiceDateA = new Date(invoiceA.date)
  const invoiceDateB = new Date(invoiceB.date)
  if (invoiceDateA > invoiceDateB) {
    return 1
  } else if (invoiceDateA < invoiceDateB) {
    return -1
  }
  return 0
}

function sortByAlphabeticalOrder(wordA: string, wordB: string) {
  if (wordA > wordB) {
    return 1
  } else if (wordA < wordB) {
    return -1
  }
  return 0
}

function sortInvoices(
  invoices: InvoiceResponseModel[],
  currentSortingColumn: InvoicesOrderedBy | null,
  sortingMode: SortingMode
) {
  switch (currentSortingColumn) {
    case InvoicesOrderedBy.DATE:
      return invoices.sort(
        (a, b) => sortByDate(a, b) * (sortingMode === SortingMode.ASC ? 1 : -1)
      )

    case InvoicesOrderedBy.REIMBURSEMENT_POINT_NAME:
      return invoices.sort(
        (a, b) =>
          sortByAlphabeticalOrder(
            a.reimbursementPointName || '',
            b.reimbursementPointName || ''
          ) * (sortingMode === SortingMode.ASC ? 1 : -1)
      )

    case InvoicesOrderedBy.REFERENCE:
      return invoices.sort(
        (a, b) =>
          sortByAlphabeticalOrder(a.reference, b.reference) *
          (sortingMode === SortingMode.ASC ? 1 : -1)
      )

    case InvoicesOrderedBy.CASHFLOW_LABELS:
      return invoices.sort(
        (a, b) =>
          sortByAlphabeticalOrder(a.cashflowLabels[0], b.cashflowLabels[0]) *
          (sortingMode === SortingMode.ASC ? 1 : -1)
      )

    case InvoicesOrderedBy.DOCUMENT_TYPE:
      return invoices.sort(
        (a, b) =>
          sortByAlphabeticalOrder(
            a.amount >= 0 ? 'a (first)' : 'z (last)',
            b.amount >= 0 ? 'a (first)' : 'z (last)'
          ) * (sortingMode === SortingMode.ASC ? 1 : -1)
      )

    default:
      return invoices.sort((a, b) => sortByDate(a, b) * -1)
  }
}

const InvoiceTable = ({ invoices }: InvoiceTableProps) => {
  const isNewBankDetailsJourneyEnabled = useActiveFeature(
    'WIP_ENABLE_NEW_BANK_DETAILS_JOURNEY'
  )
  const isFinanceIncidentEnabled = useActiveFeature(
    'WIP_ENABLE_FINANCE_INCIDENT'
  )
  const { currentSortingColumn, currentSortingMode, onColumnHeaderClick } =
    useColumnSorting<InvoicesOrderedBy>()

  const sortedInvoices = sortInvoices(
    invoices,
    currentSortingColumn,
    currentSortingMode
  )

  return (
    <table>
      <thead>
        <tr className={styles['row']}>
          <th
            scope="col"
            className={cn(styles['header'], styles['date-column'])}
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
            />
          </th>
          {isFinanceIncidentEnabled ? (
            <th
              scope="col"
              className={cn(styles['header'], styles['document-type-column'])}
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
              />
            </th>
          ) : (
            <th
              scope="col"
              className={cn(styles['header'], styles['document-type-column'])}
            >
              {isNewBankDetailsJourneyEnabled
                ? 'Compte bancaire'
                : 'Point de remboursement'}
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
          )}
          <th
            scope="col"
            className={cn(styles['header'], styles['reference-column'])}
          >
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
          <th
            scope="col"
            className={cn(styles['header'], styles['label-column'])}
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
            />
          </th>
          <th
            scope="col"
            className={cn(styles['header'], styles['amount-column'])}
          >
            Montant remboursé
          </th>
        </tr>
      </thead>
      <tbody className={styles['body']}>
        {sortedInvoices.map((invoice) => {
          return (
            <tr key={invoice.reference} className={styles['row']}>
              <td
                className={cn(
                  styles['data'],
                  styles['date-column'],
                  styles['date-data']
                )}
              >
                {format(new Date(invoice.date.replace('-', '/')), 'dd/MM/yyyy')}
              </td>
              {isFinanceIncidentEnabled ? (
                <td
                  className={cn(
                    styles['data'],
                    styles['document-type-column'],
                    styles['document-type-data']
                  )}
                >
                  {invoice.amount >= 0 ? (
                    <>
                      <SvgIcon
                        src={strokeMoreIcon}
                        alt=""
                        className={styles['more-icon']}
                        width="16"
                      />
                      Justificatif de remboursement
                    </>
                  ) : (
                    <>
                      <SvgIcon
                        src={strokeLessIcon}
                        alt=""
                        className={styles['less-icon']}
                        width="16"
                      />
                      Justificatif de trop perçu
                    </>
                  )}
                </td>
              ) : (
                <td
                  className={cn(styles['data'], styles['document-type-column'])}
                >
                  {invoice.reimbursementPointName}
                </td>
              )}
              <td className={cn(styles['data'], styles['reference-column'])}>
                {invoice.reference}
              </td>
              {/* For now only one label is possible by invoice. */}
              <td className={cn(styles['data'], styles['label-column'])}>
                {invoice.amount >= 0 ? invoice.cashflowLabels[0] : 'N/A'}
              </td>
              <td
                className={cn(
                  styles['data'],
                  styles['amount-column'],
                  styles['amount-data'],
                  {
                    [styles['negative-amount']]: invoice.amount < 0,
                  }
                )}
              >
                {formatPrice(invoice.amount, {
                  signDisplay: 'always',
                })}
              </td>
              <td className={cn(styles['data'], styles['invoice-data'])}>
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
  )
}

export default InvoiceTable
