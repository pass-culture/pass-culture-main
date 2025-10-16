import { useAnalytics } from '@/app/App/analytics/firebase'
import type { PreFiltersParams } from '@/commons/core/Bookings/types'
import { Events } from '@/commons/core/FirebaseEvents/constants'
import fullDownloadIcon from '@/icons/full-download.svg'
import { Button } from '@/ui-kit/Button/Button'
import { ButtonVariant } from '@/ui-kit/Button/types'
import { DropdownButton } from '@/ui-kit/DropdownButton/DropdownButton'

import styles from './MultiDownloadButtonsModal.module.scss'

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

  return (
    <DropdownButton
      name="Télécharger"
      triggerProps={{
        onClick: () =>
          logEvent(Events.CLICKED_DOWNLOAD_BOOKINGS, {
            from: location.pathname,
          }),
        className: styles['download-button'],
        disabled: isDownloading || isLocalLoading || isFiltersDisabled,
      }}
      options={[
        {
          id: 'excel',
          element: (
            <Button
              variant={ButtonVariant.TERNARY}
              icon={fullDownloadIcon}
              onClick={async () => {
                await downloadFunction(filters, 'XLS')
                logEvent(Events.CLICKED_DOWNLOAD_BOOKINGS_XLS, {
                  from: location.pathname,
                })
              }}
            >
              Microsoft Excel (.xls)
            </Button>
          ),
        },
        {
          id: 'csv',
          element: (
            <Button
              variant={ButtonVariant.TERNARY}
              icon={fullDownloadIcon}
              onClick={async () => {
                await downloadFunction(filters, 'CSV')
                logEvent(Events.CLICKED_DOWNLOAD_BOOKINGS_CSV, {
                  from: location.pathname,
                })
              }}
            >
              Fichier CSV (.csv)
            </Button>
          ),
        },
      ]}
    />
  )
}
