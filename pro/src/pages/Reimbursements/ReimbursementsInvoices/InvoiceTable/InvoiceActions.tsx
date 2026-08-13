import { useState } from 'react'

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
  IconPositionEnum,
} from '@/design-system/Button/types'
import { Dropdown } from '@/design-system/Dropdown/Dropdown'
import fullDownIcon from '@/icons/full-down.svg'
import fullDownloadIcon from '@/icons/full-download.svg'
import fullUpIcon from '@/icons/full-up.svg'

type InvoiceActionsProps = {
  invoice: InvoiceResponseV2Model
}

export function InvoiceActions({ invoice }: Readonly<InvoiceActionsProps>) {
  const snackBar = useSnackBar()
  const { logEvent } = useAnalytics()

  const [isOpen, setIsOpen] = useState<boolean>(false)

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
      label="Télécharger"
      items={[
        [
          {
            text: 'Télécharger le justificatif (.pdf)',
            icon: fullDownloadIcon,
            onSelect: () => downloadPDFFile(invoice.url),
          },
          {
            text: 'Télécharger le détail des réservations (.csv)',
            icon: fullDownloadIcon,
            onSelect: () => downloadCSVFile(invoice.reference),
          },
        ],
      ]}
      width={383}
      trigger={
        <Button
          label="Télécharger"
          variant={ButtonVariant.SECONDARY}
          size={ButtonSize.SMALL}
          color={ButtonColor.NEUTRAL}
          icon={isOpen ? fullUpIcon : fullDownIcon}
          iconPosition={IconPositionEnum.RIGHT}
        />
      }
      open={isOpen}
      onOpenChange={setIsOpen}
      side="right"
      align="start"
    />
  )
}
