import cn from 'classnames'
import { compareAsc, format } from 'date-fns'
import { useState } from 'react'

import { api } from 'apiClient/api'
import { InvoiceResponseV2Model } from 'apiClient/v1'
import { useAnalytics } from 'app/App/analytics/firebase'
import { SortArrow } from 'components/StocksEventList/SortArrow'
import { Events } from 'core/FirebaseEvents/constants'
import { GET_DATA_ERROR_MESSAGE } from 'core/shared/constants'
import {
  SortingMode,
  giveSortingModeForAlly,
  useColumnSorting,
} from 'hooks/useColumnSorting'
import { useNotification } from 'hooks/useNotification'
import fullDownloadIcon from 'icons/full-download.svg'
import strokeLessIcon from 'icons/stroke-less.svg'
import strokeMoreIcon from 'icons/stroke-more.svg'
import { Button } from 'ui-kit/Button/Button'
import { ButtonVariant } from 'ui-kit/Button/types'
import {
  BaseCheckbox,
  PartialCheck,
} from 'ui-kit/form/shared/BaseCheckbox/BaseCheckbox'
import { SvgIcon } from 'ui-kit/SvgIcon/SvgIcon'
import { FORMAT_DD_MM_YYYY } from 'utils/date'
import { downloadFile } from 'utils/downloadFile'
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
      return [...invoices].sort((a, b) => {
        if (a.cashflowLabels.length === 0 || b.cashflowLabels.length === 0) {
          return 0
        }
        return sortingMode === SortingMode.ASC
          ? a.cashflowLabels[0]!.localeCompare(b.cashflowLabels[0]!)
          : b.cashflowLabels[0]!.localeCompare(a.cashflowLabels[0]!)
      })

    default:
      return invoices
  }
}

export const InvoiceTable = ({ invoices }: InvoiceTableProps) => {
  const notify = useNotification()
  const { logEvent } = useAnalytics()

  const [checkedInvoices, setCheckedInvoices] = useState<string[]>([])
  const { currentSortingColumn, currentSortingMode, onColumnHeaderClick } =
    useColumnSorting<InvoicesOrderedBy>()
  const [allInvoicesChecked, setAllInvoicesChecked] = useState<PartialCheck>(
    PartialCheck.UNCHECKED
  )

  const sortedInvoices = sortInvoices(
    invoices,
    currentSortingColumn,
    currentSortingMode
  )

  function onInvoiceCheckChange(reference: string) {
    if (checkedInvoices.includes(reference)) {
      setCheckedInvoices(checkedInvoices.filter((ref) => ref !== reference))
      if (checkedInvoices.length === 1) {
        setAllInvoicesChecked(PartialCheck.UNCHECKED)
      } else if (allInvoicesChecked === PartialCheck.CHECKED) {
        setAllInvoicesChecked(PartialCheck.PARTIAL)
      }
    } else {
      setCheckedInvoices([...checkedInvoices, reference])
      if (checkedInvoices.length === invoices.length - 1) {
        setAllInvoicesChecked(PartialCheck.CHECKED)
      } else {
        setAllInvoicesChecked(PartialCheck.PARTIAL)
      }
    }
  }

  function onAllInvoicesCheckChange() {
    if (allInvoicesChecked === PartialCheck.CHECKED) {
      setAllInvoicesChecked(PartialCheck.UNCHECKED)
      setCheckedInvoices([])
    } else {
      setAllInvoicesChecked(PartialCheck.CHECKED)
      setCheckedInvoices(invoices.map((i) => i.reference))
    }
  }

  async function downloadCSVFiles(references: string[]) {
    try {
      logEvent(Events.CLICKED_INVOICES_DOWNLOAD, {
        fileType: 'details',
        filesCount: references.length,
        buttonType: 'multiple',
      })
      downloadFile(
        await api.getReimbursementsCsvV2(references),
        'remboursements_pass_culture.csv'
      )
    } catch (error) {
      notify.error(GET_DATA_ERROR_MESSAGE)
    }
  }

  async function downloadInvoices(references: string[]) {
    if (references.length > 24) {
      notify.error(
        'Vous ne pouvez pas télécharger plus de 24 documents en une fois.'
      )
      return
    }
    try {
      logEvent(Events.CLICKED_INVOICES_DOWNLOAD, {
        fileType: 'justificatif',
        filesCount: references.length,
        buttonType: 'multiple',
      })
      downloadFile(
        await api.getCombinedInvoices(references),
        'justificatif_remboursement_pass_culture.pdf'
      )
    } catch {
      notify.error(GET_DATA_ERROR_MESSAGE)
    }
  }

  return (
    <>
      <div className={styles['download-actions']} aria-live="polite">
        <BaseCheckbox
          label="Tout sélectionner"
          checked={allInvoicesChecked !== PartialCheck.UNCHECKED}
          partialCheck={allInvoicesChecked === PartialCheck.PARTIAL}
          onChange={onAllInvoicesCheckChange}
        />
        {checkedInvoices.length > 0 && (
          <>
            <Button
              variant={ButtonVariant.TERNARY}
              icon={fullDownloadIcon}
              onClick={() => downloadInvoices(checkedInvoices)}
              className={styles['first-action']}
            >
              Télécharger les justificatifs
            </Button>
            <Button
              variant={ButtonVariant.TERNARY}
              icon={fullDownloadIcon}
              onClick={() => downloadCSVFiles(checkedInvoices)}
            >
              Télécharger les détails
            </Button>
          </>
        )}
      </div>
      <table role="table" className={styles['invoices-table']}>
        <caption className="visually-hidden">
          Justificatif de remboursement ou de trop perçu
        </caption>
        <thead className={styles['header']}>
          <tr role="row" data-testid="invoice-title-row">
            <th
              role="columnheader"
              scope="col"
              className={styles['header-cell']}
              colSpan={2}
            >
              <div className={styles['header-sort']}>
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
              </div>
            </th>

            <th
              role="columnheader"
              scope="col"
              className={styles['header-cell']}
            >
              <div className={styles['header-sort']}>
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
              </div>
            </th>
            <th
              role="columnheader"
              scope="col"
              className={cn(
                styles['header-cell'],
                styles['bank-account-column']
              )}
            >
              <div className={styles['header-sort']}>
                Compte bancaire
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
                      Tri par compte bancaire
                      {giveSortingModeForAlly(currentSortingMode)} activé.
                    </span>
                  )}
                </SortArrow>
              </div>
            </th>
            <th
              role="columnheader"
              scope="col"
              className={styles['header-cell']}
            >
              <div className={styles['header-sort']}>
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
                  {currentSortingColumn ===
                    InvoicesOrderedBy.CASHFLOW_LABELS && (
                    <span className="visually-hidden">
                      Tri par n° de virement{' '}
                      {giveSortingModeForAlly(currentSortingMode)} activé.
                    </span>
                  )}
                </SortArrow>
              </div>
            </th>
            <th
              role="columnheader"
              scope="col"
              className={cn(styles['header-cell'], styles['amount-column'])}
            >
              Montant remboursé
            </th>
            <th
              role="columnheader"
              scope="col"
              className={styles['header-cell']}
            >
              Actions
            </th>
          </tr>
        </thead>
        <tbody className={styles['body']}>
          {sortedInvoices.map((invoice) => {
            return (
              <tr
                role="row"
                key={invoice.reference}
                className={styles['row']}
                data-testid="invoice-item-row"
              >
                <td
                  role="cell"
                  className={styles['data']}
                  data-label="Sélection du justificatif"
                >
                  <BaseCheckbox
                    checked={checkedInvoices.includes(invoice.reference)}
                    onChange={() => onInvoiceCheckChange(invoice.reference)}
                    label={`Sélection du ${invoice.amount >= 0 ? 'remboursement' : 'trop perçu'} du ${format(new Date(invoice.date), FORMAT_DD_MM_YYYY)}`}
                    exceptionnallyHideLabelDespiteA11y
                  />
                </td>
                <td
                  role="cell"
                  className={cn(styles['data'], styles['date-data'])}
                  data-label="Date du justificatif"
                >
                  {format(new Date(invoice.date), FORMAT_DD_MM_YYYY)}
                </td>
                <td
                  role="cell"
                  className={styles['data']}
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
                  className={styles['data']}
                  data-label="N° de virement"
                >
                  {invoice.amount >= 0 ? invoice.cashflowLabels[0] : 'N/A'}
                </td>
                <td
                  role="cell"
                  className={cn(styles['data'], styles['amount-column'], {
                    [styles['negative-amount'] ?? '']: invoice.amount < 0,
                  })}
                  data-label="Montant remboursé"
                >
                  {formatPrice(invoice.amount, {
                    signDisplay: 'always',
                  })}
                </td>
                <td role="cell" className={styles['data']} data-label="Actions">
                  <InvoiceActions invoice={invoice} />
                </td>
              </tr>
            )
          })}
        </tbody>
      </table>
    </>
  )
}
