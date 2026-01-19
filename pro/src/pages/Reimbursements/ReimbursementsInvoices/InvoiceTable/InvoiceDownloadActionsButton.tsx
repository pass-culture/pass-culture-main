import { api } from '@/apiClient/api'
import { useAnalytics } from '@/app/App/analytics/firebase'
import { Events } from '@/commons/core/FirebaseEvents/constants'
import { GET_DATA_ERROR_MESSAGE } from '@/commons/core/shared/constants'
import { useSnackBar } from '@/commons/hooks/useSnackBar'
import { downloadFile } from '@/commons/utils/downloadFile'
import { Button } from '@/design-system/Button/Button'
import { ButtonColor, ButtonVariant } from '@/design-system/Button/types'
import fullDownloadIcon from '@/icons/full-download.svg'

import styles from './InvoiceDownloadActionsButton.module.scss'

type InvoiceDownloadActionsButtonProps = {
  checkedInvoices: string[]
}

export const MAX_ITEMS_DOWNLOAD = 75

export const InvoiceDownloadActionsButton = ({
  checkedInvoices,
}: InvoiceDownloadActionsButtonProps) => {
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
        await api.getReimbursementsCsvV2(references),
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
        await api.getCombinedInvoices(references),
        'justificatif_remboursement_pass_culture.pdf'
      )
    } catch {
      snackBar.error(GET_DATA_ERROR_MESSAGE)
    }
  }

  return (
    <div className={styles['download-actions']} aria-live="polite">
      {checkedInvoices.length > 0 && (
        <>
          <Button
            variant={ButtonVariant.TERTIARY}
            color={ButtonColor.NEUTRAL}
            icon={fullDownloadIcon}
            onClick={() => downloadInvoices(checkedInvoices)}
            className={styles['first-action']}
            label="Télécharger les justificatifs"
          />
          <Button
            variant={ButtonVariant.TERTIARY}
            color={ButtonColor.NEUTRAL}
            icon={fullDownloadIcon}
            onClick={() => downloadCSVFiles(checkedInvoices)}
            label="Télécharger les détails"
          />
        </>
      )}
    </div>
  )
}
