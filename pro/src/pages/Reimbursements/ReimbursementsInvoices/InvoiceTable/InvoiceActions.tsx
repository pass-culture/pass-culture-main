import * as DropdownMenu from '@radix-ui/react-dropdown-menu'

import { api } from 'apiClient/api'
import { InvoiceResponseV2Model } from 'apiClient/v1'
import { GET_DATA_ERROR_MESSAGE } from 'core/shared/constants'
import { useNotification } from 'hooks/useNotification'
import fullDownloadIcon from 'icons/full-download.svg'
import fullOtherIcon from 'icons/full-other.svg'
import { ButtonLink } from 'ui-kit/Button/ButtonLink'
import { ButtonVariant } from 'ui-kit/Button/types'
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
    <DropdownMenu.Root>
      <DropdownMenu.Trigger
        className={styles['menu-button']}
        title="Téléchargment des justificatifs"
        data-testid="invoice-actions-button"
      >
        <SvgIcon
          src={fullOtherIcon}
          alt="Téléchargment des justificatifs"
          className={styles['menu-button-icon']}
        />
      </DropdownMenu.Trigger>
      <DropdownMenu.Portal>
        <DropdownMenu.Content className={styles['menu-list']} align="end">
          <DropdownMenu.Item
            className={styles['menu-item']}
            title={'Télécharger le justificatif comptable (.pdf)'}
          >
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
          </DropdownMenu.Item>
          <DropdownMenu.Item
            className={styles['menu-item']}
            onSelect={() => downloadCSVFile(invoice.reference)}
            title={'Télécharger le détail des réservations (.csv)'}
          >
            <SvgIcon
              src={fullDownloadIcon}
              alt=""
              className={styles['menu-item-icon']}
              width="20"
            />
            <span>{'Télécharger le détail des réservations (.csv)'}</span>
          </DropdownMenu.Item>
        </DropdownMenu.Content>
      </DropdownMenu.Portal>
    </DropdownMenu.Root>
  )
}
