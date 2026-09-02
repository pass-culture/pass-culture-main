import { api } from '@/apiClient/api'
import { useAnalytics } from '@/app/App/analytics/firebase'
import { Events } from '@/commons/core/FirebaseEvents/constants'
import { GET_DATA_ERROR_MESSAGE } from '@/commons/core/shared/constants'
import { useSnackBar } from '@/commons/hooks/useSnackBar'
import { downloadFile } from '@/commons/utils/downloadFile'
import { pluralizeFr } from '@/commons/utils/pluralize'
import { ActionsBarSticky } from '@/components/ActionsBarSticky/ActionsBarSticky'
import { Button } from '@/design-system/Button/Button'
import { ButtonVariant } from '@/design-system/Button/types'

import { DOWNLOAD_REIMBURSEMENTS_LABEL } from '../constants'
import styles from './InvoiceDownloadActionsBar.module.scss'

type InvoiceDownloadActionsBarProps = {
  checkedInvoices: string[]
}

export const MAX_ITEMS_DOWNLOAD = 75

export const InvoiceDownloadActionsBar = ({
  checkedInvoices,
}: InvoiceDownloadActionsBarProps) => {
  const snackBar = useSnackBar()
  const { logEvent } = useAnalytics()
  async function downloadCSVFiles(references: string[]) {
    if (references.length > MAX_ITEMS_DOWNLOAD) {
      snackBar.error(
        `Vous ne pouvez pas télécharger plus de ${MAX_ITEMS_DOWNLOAD} documents en une fois.`
      )
      return
    }
    try {
      logEvent(Events.CLICKED_INVOICES_DOWNLOAD, {
        fileType: 'details',
        filesCount: references.length,
        buttonType: 'multiple',
      })
      downloadFile(
        (await api.getReimbursementsCsvV2({
          query: {
            invoicesReferences: references,
          },
          parseAs: 'blob',
        })) as Blob,
        'remboursements_pass_culture.csv'
      )
    } catch {
      snackBar.error(GET_DATA_ERROR_MESSAGE)
    }
  }

  async function downloadInvoices(references: string[]) {
    if (references.length > MAX_ITEMS_DOWNLOAD) {
      snackBar.error(
        `Vous ne pouvez pas télécharger plus de ${MAX_ITEMS_DOWNLOAD} documents en une fois.`
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
        (await api.getCombinedInvoices({
          query: {
            invoiceReferences: references,
          },
        })) as Blob,
        'justificatif_remboursement_pass_culture.pdf'
      )
    } catch {
      snackBar.error(GET_DATA_ERROR_MESSAGE)
    }
  }

  const checkedInvoicesCountText = `${checkedInvoices.length} ${pluralizeFr(checkedInvoices.length, 'justificatif sélectionné', 'justificatifs sélectionnés')}`

  return (
    <div aria-live="polite">
      {checkedInvoices.length > 0 && (
        <ActionsBarSticky isEmbedded>
          <ActionsBarSticky.Left>
            <p className={styles['checked-invoice-count']}>
              {checkedInvoicesCountText}
            </p>
          </ActionsBarSticky.Left>
          <ActionsBarSticky.Right>
            <Button
              variant={ButtonVariant.SECONDARY}
              onClick={() => downloadCSVFiles(checkedInvoices)}
              label={DOWNLOAD_REIMBURSEMENTS_LABEL}
            />
            <Button
              variant={ButtonVariant.PRIMARY}
              onClick={() => downloadInvoices(checkedInvoices)}
              label="Télécharger les justificatifs (.pdf)"
            />
          </ActionsBarSticky.Right>
        </ActionsBarSticky>
      )}
    </div>
  )
}
