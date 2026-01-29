import { useAnalytics } from '@/app/App/analytics/firebase'
import type { PreFiltersParams } from '@/commons/core/Bookings/types'
import { Events } from '@/commons/core/FirebaseEvents/constants'
import { Button } from '@/design-system/Button/Button'
import { ButtonColor, ButtonVariant } from '@/design-system/Button/types'
import fullDownloadIcon from '@/icons/full-download.svg'
import { DropdownButton } from '@/ui-kit/DropdownButton/DropdownButton'

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
    <div>
      <DropdownButton
        name="Télécharger"
        triggerProps={{
          onClick: () =>
            logEvent(Events.CLICKED_DOWNLOAD_BOOKINGS, {
              from: location.pathname,
            }),
          disabled: isDownloading || isLocalLoading || isFiltersDisabled,
        }}
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
      />
    </div>
  )
}
