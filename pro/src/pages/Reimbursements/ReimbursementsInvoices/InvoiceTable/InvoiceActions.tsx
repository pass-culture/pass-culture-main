import { api } from 'apiClient/api'
import { InvoiceResponseV2Model } from 'apiClient/v1'
import { GET_DATA_ERROR_MESSAGE } from 'core/shared/constants'
import { useNotification } from 'hooks/useNotification'
import fullDownloadIcon from 'icons/full-download.svg'
import { ButtonLink } from 'ui-kit/Button/ButtonLink'
import { ButtonVariant } from 'ui-kit/Button/types'
import { DropdownItem } from 'ui-kit/DropdownMenuWrapper/DropdownItem'
import { DropdownMenuWrapper } from 'ui-kit/DropdownMenuWrapper/DropdownMenuWrapper'
import { SvgIcon } from 'ui-kit/SvgIcon/SvgIcon'
import { downloadFile } from 'utils/downloadFile'

import styles from './InvoiceTable.module.scss'

type InvoiceActionsProps = {
  invoice: InvoiceResponseV2Model
}

export function InvoiceActions({ invoice }: InvoiceActionsProps) {
  const notify = useNotification()

  async function downloadCSVFile(reference: string) {
    try {
      downloadFile(
        await api.getReimbursementsCsvV2([reference]),
        'remboursements_pass_culture'
      )
    } catch {
      notify.error(GET_DATA_ERROR_MESSAGE)
    }
  }

  return (
    <DropdownMenuWrapper title="Téléchargment des justificatifs">
      <>
        <DropdownItem title="Télécharger le justificatif comptable (.pdf)">
          <ButtonLink
            link={{
              isExternal: true,
              to: invoice.url,
              target: '_blank',
              download: true,
            }}
            icon={fullDownloadIcon}
            svgAlt=""
            variant={ButtonVariant.TERNARY}
          >
            Télécharger le justificatif comptable (.pdf)
          </ButtonLink>
        </DropdownItem>
        <DropdownItem
          title="Télécharger le détail des réservations (.csv)"
          onSelect={() => downloadCSVFile(invoice.reference)}
        >
          <SvgIcon
            src={fullDownloadIcon}
            alt=""
            className={styles['menu-item-icon']}
            width="20"
          />
          <span>Télécharger le détail des réservations (.csv)</span>
        </DropdownItem>
      </>
    </DropdownMenuWrapper>
  )
}
