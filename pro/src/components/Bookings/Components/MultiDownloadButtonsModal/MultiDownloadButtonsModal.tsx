import { useState } from 'react'

import { useAnalytics } from '@/app/App/analytics/firebase'
import type { PreFiltersParams } from '@/commons/core/Bookings/types'
import { Events } from '@/commons/core/FirebaseEvents/constants'
import { Button } from '@/design-system/Button/Button'
import { ButtonVariant, IconPositionEnum } from '@/design-system/Button/types'
import fullDownIcon from '@/icons/full-down.svg'
import fullDownloadIcon from '@/icons/full-download.svg'
import fullUpIcon from '@/icons/full-up.svg'
import { Dropdown } from '@/ui-kit/Dropdown/Dropdown'
import { DropdownItem } from '@/ui-kit/Dropdown/DropdownItem'

type MultiDownloadButtonsModalType = {
  isDownloading: boolean
  isLocalLoading: boolean
  isFiltersDisabled: boolean
  downloadFunction: (
    filters: PreFiltersParams,
    type: 'CSV' | 'XLS'
  ) => Promise<void>
  filters: PreFiltersParams
}

export const MultiDownloadButtonsModal = ({
  isDownloading,
  isLocalLoading,
  isFiltersDisabled,
  downloadFunction,
  filters,
}: MultiDownloadButtonsModalType): JSX.Element => {
  const { logEvent } = useAnalytics()
  const [isOpen, setIsOpen] = useState(false)

  return (
    <Dropdown
      title="Télécharger les réservations"
      open={isOpen}
      onOpenChange={setIsOpen}
      align="start"
      trigger={
        <Button
          label="Télécharger"
          variant={ButtonVariant.PRIMARY}
          icon={isOpen ? fullUpIcon : fullDownIcon}
          iconPosition={IconPositionEnum.RIGHT}
          onClick={() =>
            logEvent(Events.CLICKED_DOWNLOAD_BOOKINGS, {
              from: location.pathname,
            })
          }
          disabled={isDownloading || isLocalLoading || isFiltersDisabled}
        />
      }
    >
      <DropdownItem
        title="Microsoft Excel (.xls)"
        icon={fullDownloadIcon}
        onSelect={async () => {
          await downloadFunction(filters, 'XLS')
          logEvent(Events.CLICKED_DOWNLOAD_BOOKINGS_XLS, {
            from: location.pathname,
          })
        }}
      />
      <DropdownItem
        title="Fichier CSV (.csv)"
        icon={fullDownloadIcon}
        onSelect={async () => {
          await downloadFunction(filters, 'CSV')
          logEvent(Events.CLICKED_DOWNLOAD_BOOKINGS_CSV, {
            from: location.pathname,
          })
        }}
      />
    </Dropdown>
  )
}
