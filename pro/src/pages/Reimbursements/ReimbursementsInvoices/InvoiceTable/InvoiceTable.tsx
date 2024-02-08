import * as Sentry from '@sentry/react'
import cn from 'classnames'
import { compareAsc, format } from 'date-fns'

import { InvoiceResponseModel } from 'apiClient/v1'
import { SortArrow } from 'components/StocksEventList/SortArrow'
import useActiveFeature from 'hooks/useActiveFeature'
import {
  SortingMode,
  giveSortingModeForAlly,
  useColumnSorting,
} from 'hooks/useColumnSorting'
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

function sortInvoices(
  invoices: InvoiceResponseModel[],
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
          ? (a.reimbursementPointName ?? '').localeCompare(
              b.reimbursementPointName ?? ''
            )
          : (b.reimbursementPointName ?? '').localeCompare(
              a.reimbursementPointName ?? ''
            )
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

  sortedInvoices.forEach((invoice) => {
    try {
      format(new Date(invoice.date.replace('-', '/')), 'dd/MM/yyyy')
    } catch (error) {
      Sentry.addBreadcrumb({
        message: 'Invalid date',
        level: 'info',
        data: { invoiceId: invoice.reference, date: invoice.date },
      })
      Sentry.captureException(error)
    }
  })

  return (
    <table role="table" className={styles['invoices-table']}>
      <caption className="visually-hidden">
        Justificatif de remboursement ou de trop perçu
      </caption>
      <thead>
        <tr role="row" className={styles['row']}>
          <th
            role="columnheader"
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
            >
              {currentSortingColumn === InvoicesOrderedBy.DATE && (
                <span className="visually-hidden">
                  Tri par date {giveSortingModeForAlly(currentSortingMode)}{' '}
                  activé.
                </span>
              )}
            </SortArrow>
          </th>
          {isFinanceIncidentEnabled ? (
            <th
              role="columnheader"
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
              >
                {currentSortingColumn === InvoicesOrderedBy.DOCUMENT_TYPE && (
                  <span className="visually-hidden">
                    Tri par type de document{' '}
                    {giveSortingModeForAlly(currentSortingMode)} activé.
                  </span>
                )}
              </SortArrow>
            </th>
          ) : (
            <th
              role="columnheader"
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
              >
                {currentSortingColumn ===
                  InvoicesOrderedBy.REIMBURSEMENT_POINT_NAME && (
                  <span className="visually-hidden">
                    Tri par{' '}
                    {isNewBankDetailsJourneyEnabled
                      ? 'compte bancaire '
                      : 'point de remboursement '}
                    {giveSortingModeForAlly(currentSortingMode)} activé.
                  </span>
                )}
              </SortArrow>
            </th>
          )}
          <th
            role="columnheader"
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
            >
              {currentSortingColumn === InvoicesOrderedBy.REFERENCE && (
                <span className="visually-hidden">
                  Tri par n° de justificatif{' '}
                  {giveSortingModeForAlly(currentSortingMode)} activé.
                </span>
              )}
            </SortArrow>
          </th>
          <th
            role="columnheader"
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
            className={cn(styles['header'], styles['amount-column'])}
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
                {invoice.date}
                {/* This line is causing a bug, waiting for Sentry details to decomment it */}
                {/* {format(new Date(invoice.date.replace('-', '/')), 'dd/MM/yyyy')} */}
              </td>
              {isFinanceIncidentEnabled ? (
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
                      Justificatif de remboursement
                    </span>
                  ) : (
                    <span className={styles['document-type-content']}>
                      <SvgIcon
                        src={strokeLessIcon}
                        alt=""
                        className={styles['less-icon']}
                        width="16"
                      />
                      Justificatif de&nbsp;trop&nbsp;perçu
                    </span>
                  )}
                </td>
              ) : (
                <td
                  role="cell"
                  className={cn(styles['data'], styles['document-type-column'])}
                  data-label="Point de remboursement"
                >
                  {invoice.reimbursementPointName}
                </td>
              )}
              <td
                role="cell"
                className={cn(styles['data'], styles['reference-column'])}
                data-label="N° du justificatif"
              >
                {invoice.reference}
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
                className={cn(styles['data'], styles['invoice-data'])}
                data-label="Téléchargement"
              >
                <ButtonLink
                  link={{
                    isExternal: true,
                    to: invoice.url,
                    target: '_blank',
                    download: true,
                  }}
                  icon={fullDownloadIcon}
                  svgAlt={`Justificatif de ${
                    invoice.amount >= 0 ? 'remboursement' : 'trop perçu'
                  } ${invoice.reference}, nouvelle fenêtre, format`}
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
