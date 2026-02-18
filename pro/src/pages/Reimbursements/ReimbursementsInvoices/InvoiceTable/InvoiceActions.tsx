import { api } from '@/apiClient/api'
import type { InvoiceResponseV2Model } from '@/apiClient/v1'
import { useAnalytics } from '@/app/App/analytics/firebase'
import { Events } from '@/commons/core/FirebaseEvents/constants'
import { GET_DATA_ERROR_MESSAGE } from '@/commons/core/shared/constants'
import { useSnackBar } from '@/commons/hooks/useSnackBar'
import { downloadFile } from '@/commons/utils/downloadFile'
import fullDownloadIcon from '@/icons/full-download.svg'
import { Dropdown } from '@/ui-kit/Dropdown/Dropdown'
import { DropdownItem } from '@/ui-kit/Dropdown/DropdownItem'

type InvoiceActionsProps = {
  invoice: InvoiceResponseV2Model
}

export function InvoiceActions({ invoice }: InvoiceActionsProps) {
  const snackBar = useSnackBar()
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
      snackBar.error(GET_DATA_ERROR_MESSAGE)
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
      snackBar.error(GET_DATA_ERROR_MESSAGE)
    }
  }

  return (
    <Dropdown title="Téléchargement des justificatifs" triggerTooltip>
      <DropdownItem
        title="Télécharger le justificatif comptable (.pdf)"
        icon={fullDownloadIcon}
        onSelect={() => downloadPDFFile(invoice.url)}
      />
      <DropdownItem
        title="Télécharger le détail des réservations (.csv)"
        icon={fullDownloadIcon}
        onSelect={() => downloadCSVFile(invoice.reference)}
      />
    </Dropdown>
  )
}
