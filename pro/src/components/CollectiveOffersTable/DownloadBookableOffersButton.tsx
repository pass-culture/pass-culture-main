import { useState } from 'react'

import type { CollectiveSearchFiltersParams } from '@/commons/core/Offers/types'
import { GET_DATA_ERROR_MESSAGE } from '@/commons/core/shared/constants'
import { useNotification } from '@/commons/hooks/useNotification'
import { downloadBookableOffersFile } from '@/components/CollectiveOffersTable/utils/downloadBookableOffersFile'
import fullDownloadIcon from '@/icons/full-download.svg'
import { Button } from '@/ui-kit/Button/Button'
import { ButtonVariant } from '@/ui-kit/Button/types'
import { DropdownButton } from '@/ui-kit/DropdownButton/DropdownButton'

type DownloadBookableOffersButtonProps = {
  isDisabled: boolean
  filters: CollectiveSearchFiltersParams
  defaultFilters: CollectiveSearchFiltersParams
}

export const DownloadBookableOffersButton = ({
  isDisabled,
  filters,
  defaultFilters,
}: DownloadBookableOffersButtonProps): JSX.Element => {
  const notify = useNotification()
  const [isDownloading, setIsDownloading] = useState(false)

  const downloadHandler = async (type: 'CSV' | 'XLS'): Promise<void> => {
    setIsDownloading(true)

    try {
      await downloadBookableOffersFile(filters, defaultFilters, type)
    } catch {
      notify.error(GET_DATA_ERROR_MESSAGE)
    }

    setIsDownloading(false)
  }

  return (
    <DropdownButton
      name="Télécharger"
      triggerProps={{
        variant: ButtonVariant.TERNARY,
        icon: fullDownloadIcon,
        disabled: isDownloading || isDisabled,
      }}
      options={[
        {
          id: 'excel',
          element: (
            <Button
              variant={ButtonVariant.TERNARY}
              icon={fullDownloadIcon}
              onClick={async () => {
                await downloadHandler('XLS')
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
                await downloadHandler('CSV')
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
