import { api } from '@/apiClient/api'
import { useAnalytics } from '@/app/App/analytics/firebase'
import { Events } from '@/commons/core/FirebaseEvents/constants'
import { GET_DATA_ERROR_MESSAGE } from '@/commons/core/shared/constants'
import { useNotification } from '@/commons/hooks/useNotification'
import { downloadFile } from '@/commons/utils/downloadFile'
import fullDownloadIcon from '@/icons/full-download.svg'
import { Button } from '@/ui-kit/Button/Button'
import { ButtonVariant } from '@/ui-kit/Button/types'

import styles from './InvoiceDownloadActionsButton.module.scss'

type InvoiceDownloadActionsButtonProps = {
  checkedInvoices: string[]
}

export const InvoiceDownloadActionsButton = ({
  checkedInvoices,
}: InvoiceDownloadActionsButtonProps) => {
  const notify = useNotification()
  const { logEvent } = useAnalytics()
  async function downloadCSVFiles(references: string[]) {
    if (references.length > 24) {
      notify.error(
        'Vous ne pouvez pas télécharger plus de 24 documents en une fois.'
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
    <div className={styles['download-actions']} aria-live="polite">
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
  )
}
