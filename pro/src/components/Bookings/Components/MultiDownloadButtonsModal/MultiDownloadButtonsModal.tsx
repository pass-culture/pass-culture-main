import { useState } from 'react'

import { useAnalytics } from '@/app/App/analytics/firebase'
import type { PreFiltersParams } from '@/commons/core/Bookings/types'
import { Events } from '@/commons/core/FirebaseEvents/constants'
import { Button } from '@/design-system/Button/Button'
import {
  ButtonColor,
  ButtonVariant,
  IconPositionEnum,
} from '@/design-system/Button/types'
import fullDownIcon from '@/icons/full-down.svg'
import fullDownloadIcon from '@/icons/full-download.svg'
import fullUpIcon from '@/icons/full-up.svg'
import { Dropdown } from '@/ui-kit/DropdownMenuWrapper/Dropdown'

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
      open={isOpen}
      onOpenChange={setIsOpen}
      align="start"
      options={[
        {
          id: 'excel',
          element: (
            <Button
              variant={ButtonVariant.TERTIARY}
              color={ButtonColor.NEUTRAL}
              icon={fullDownloadIcon}
              onClick={async () => {
                await downloadFunction(filters, 'XLS')
                logEvent(Events.CLICKED_DOWNLOAD_BOOKINGS_XLS, {
                  from: location.pathname,
                })
              }}
              label="Microsoft Excel (.xls)"
            />
          ),
        },
        {
          id: 'csv',
          element: (
            <Button
              variant={ButtonVariant.TERTIARY}
              color={ButtonColor.NEUTRAL}
              icon={fullDownloadIcon}
              onClick={async () => {
                await downloadFunction(filters, 'CSV')
                logEvent(Events.CLICKED_DOWNLOAD_BOOKINGS_CSV, {
                  from: location.pathname,
                })
              }}
              label="Fichier CSV (.csv)"
            />
          ),
        },
      ]}
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
    />
  )
}
