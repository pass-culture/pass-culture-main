import { api } from 'apiClient/api'
import { InvoiceResponseV2Model } from 'apiClient/v1'
import { useAnalytics } from 'app/App/analytics/firebase'
import { Events } from 'core/FirebaseEvents/constants'
import { GET_DATA_ERROR_MESSAGE } from 'core/shared/constants'
import { useNotification } from 'hooks/useNotification'
import fullDownloadIcon from 'icons/full-download.svg'
import { Button } from 'ui-kit/Button/Button'
import { ButtonVariant } from 'ui-kit/Button/types'
import { DropdownItem } from 'ui-kit/DropdownMenuWrapper/DropdownItem'
import { DropdownMenuWrapper } from 'ui-kit/DropdownMenuWrapper/DropdownMenuWrapper'
import { downloadFile } from 'utils/downloadFile'

type InvoiceActionsProps = {
  invoice: InvoiceResponseV2Model
}

export function InvoiceActions({ invoice }: InvoiceActionsProps) {
  const notify = useNotification()
  const { logEvent } = useAnalytics()

  async function downloadPDFFile(url: string) {
    try {
      logEvent(Events.CLICKED_INVOICES_DOWNLOAD, {
        fileType: 'justificatif',
        filesCount: 1,
        buttonType: 'unique',
      })
      downloadFile(
        await fetch(url).then((res) => res.blob()),
        'justificatif_comptable.pdf'
      )
    } catch {
      notify.error(GET_DATA_ERROR_MESSAGE)
    }
  }

  async function downloadCSVFile(reference: string) {
    try {
      logEvent(Events.CLICKED_INVOICES_DOWNLOAD, {
        fileType: 'details',
        filesCount: 1,
        buttonType: 'unique',
      })
      downloadFile(
        await api.getReimbursementsCsvV2([reference]),
        'remboursements_pass_culture.csv'
      )
    } catch {
      notify.error(GET_DATA_ERROR_MESSAGE)
    }
  }

  return (
    <DropdownMenuWrapper title="Téléchargement des justificatifs">
      <>
        <DropdownItem
          title="Télécharger le justificatif comptable (.pdf)"
          onSelect={() => downloadPDFFile(invoice.url)}
        >
          <Button icon={fullDownloadIcon} variant={ButtonVariant.TERNARY}>
            Télécharger le justificatif comptable (.pdf)
          </Button>
        </DropdownItem>
        <DropdownItem
          title="Télécharger le détail des réservations (.csv)"
          onSelect={() => downloadCSVFile(invoice.reference)}
        >
          <Button icon={fullDownloadIcon} variant={ButtonVariant.TERNARY}>
            Télécharger le détail des réservations (.csv)
          </Button>
        </DropdownItem>
      </>
    </DropdownMenuWrapper>
  )
}
