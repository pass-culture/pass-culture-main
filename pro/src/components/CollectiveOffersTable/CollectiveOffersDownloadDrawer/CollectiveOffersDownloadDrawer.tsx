import * as Dialog from '@radix-ui/react-dialog'
import { useState } from 'react'

import type { CollectiveSearchFiltersParams } from '@/commons/core/Offers/types'
import { GET_DATA_ERROR_MESSAGE } from '@/commons/core/shared/constants'
import { useSnackBar } from '@/commons/hooks/useSnackBar'
import { downloadBookableOffersFile } from '@/components/CollectiveOffersTable/utils/downloadBookableOffersFile'
import { Banner } from '@/design-system/Banner/Banner'
import { Button } from '@/ui-kit/Button/Button'
import { ButtonVariant } from '@/ui-kit/Button/types'
import { DialogBuilder } from '@/ui-kit/DialogBuilder/DialogBuilder'

import styles from './CollectiveOffersDownloadDrawer.module.scss'

type CollectiveOffersDownloadDrawerProps = {
  isDisabled: boolean
  filters: CollectiveSearchFiltersParams
}

export const CollectiveOffersDownloadDrawer = ({
  isDisabled,
  filters,
}: CollectiveOffersDownloadDrawerProps) => {
  const snackBar = useSnackBar()
  const [isOpenDialog, setIsOpenDialog] = useState(false)
  const [isDownloading, setIsDownloading] = useState(false)

  const downloadHandler = async (type: 'CSV' | 'XLS'): Promise<void> => {
    setIsDownloading(true)

    try {
      await downloadBookableOffersFile(filters, type)
    } catch {
      snackBar.error(GET_DATA_ERROR_MESSAGE)
    }

    setIsDownloading(false)
  }

  return (
    <DialogBuilder
      variant="drawer"
      onOpenChange={setIsOpenDialog}
      open={isOpenDialog}
      title="Télécharger les offres"
      trigger={
        <Button
          variant={ButtonVariant.PRIMARY}
          disabled={isDisabled || isDownloading}
        >
          Télécharger
        </Button>
      }
    >
      <div className={styles['callout']}>
        <Banner
          title="Utilisation des filtres"
          description="Appliquez des filtres à votre tableau pour sélectionner les offres que vous souhaitez télécharger."
        />
      </div>
      <DialogBuilder.Footer>
        <div className={styles['actions']}>
          <Dialog.Close asChild>
            <Button variant={ButtonVariant.SECONDARY}>Annuler</Button>
          </Dialog.Close>
          <Button
            variant={ButtonVariant.PRIMARY}
            onClick={async () => {
              await downloadHandler('CSV')
            }}
          >
            Télécharger format CSV
          </Button>
          <Button
            variant={ButtonVariant.PRIMARY}
            onClick={async () => {
              await downloadHandler('XLS')
            }}
          >
            Télécharger format Excel
          </Button>
        </div>
      </DialogBuilder.Footer>
    </DialogBuilder>
  )
}
