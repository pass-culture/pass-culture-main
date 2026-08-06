import { api } from '@/apiClient/api'
import type { InvoiceResponseV2Model } from '@/apiClient/v1'
import { useAnalytics } from '@/app/App/analytics/firebase'
import { Events } from '@/commons/core/FirebaseEvents/constants'
import { GET_DATA_ERROR_MESSAGE } from '@/commons/core/shared/constants'
import { useSnackBar } from '@/commons/hooks/useSnackBar'
import { downloadFile } from '@/commons/utils/downloadFile'
import { Button } from '@/design-system/Button/Button'
import {
  ButtonColor,
  ButtonSize,
  ButtonVariant,
} from '@/design-system/Button/types'
import { Dropdown } from '@/design-system/Dropdown/Dropdown'
import fullDownloadIcon from '@/icons/full-download.svg'

type InvoiceActionsProps = {
  invoice: InvoiceResponseV2Model
}

import fullThreeDotsIcon from '@/icons/full-three-dots.svg'

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
        (await api.getReimbursementsCsvV2({
          query: {
            invoicesReferences: [reference],
          },
          parseAs: 'blob',
        })) as Blob,
        'remboursements_pass_culture.csv'
      )
    } catch {
      snackBar.error(GET_DATA_ERROR_MESSAGE)
    }
  }

  return (
    <Dropdown
      label="Téléchargement des justificatifs"
      trigger={
        <Button
          variant={ButtonVariant.SECONDARY}
          icon={fullThreeDotsIcon}
          size={ButtonSize.SMALL}
          color={ButtonColor.NEUTRAL}
          tooltip="Téléchargement des justificatifs"
        />
      }
      width={370}
      items={[
        [
          {
            text: 'Télécharger le justificatif comptable (.pdf)',
            icon: fullDownloadIcon,
            onClick: () => downloadPDFFile(invoice.url),
          },
          {
            text: 'Télécharger le détail des réservations (.csv)',
            icon: fullDownloadIcon,
            onClick: () => downloadCSVFile(invoice.reference),
          },
        ],
      ]}
    />
  )
}
