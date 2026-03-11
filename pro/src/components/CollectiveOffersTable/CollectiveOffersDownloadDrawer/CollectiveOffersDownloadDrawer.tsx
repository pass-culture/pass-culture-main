import * as Dialog from '@radix-ui/react-dialog'
import { useState } from 'react'
import { useLocation } from 'react-router'

import { useAnalytics } from '@/app/App/analytics/firebase'
import { Events } from '@/commons/core/FirebaseEvents/constants'
import type { CollectiveSearchFiltersParams } from '@/commons/core/Offers/types'
import { GET_DATA_ERROR_MESSAGE } from '@/commons/core/shared/constants'
import { useSnackBar } from '@/commons/hooks/useSnackBar'
import { downloadBookableOffersFile } from '@/components/CollectiveOffersTable/utils/downloadBookableOffersFile'
import { Banner } from '@/design-system/Banner/Banner'
import { Button } from '@/design-system/Button/Button'
import { ButtonColor, ButtonVariant } from '@/design-system/Button/types'
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
  const { logEvent } = useAnalytics()
  const location = useLocation()

  const downloadHandler = async (
    type: 'CSV' | 'XLS',
    eventToLog: string
  ): Promise<void> => {
    setIsDownloading(true)

    try {
      logEvent(eventToLog, { from: location.pathname })
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
          variant={ButtonVariant.SECONDARY}
          disabled={isDisabled || isDownloading}
          onClick={() =>
            logEvent(Events.CLICKED_DOWNLOAD_COLLECTIVE_OFFERS, {
              from: location.pathname,
            })
          }
          label="Télécharger"
        />
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
            <Button
              variant={ButtonVariant.SECONDARY}
              color={ButtonColor.NEUTRAL}
              label="Annuler"
            />
          </Dialog.Close>
          <Button
            variant={ButtonVariant.PRIMARY}
            onClick={async () => {
              await downloadHandler(
                'CSV',
                Events.CLICKED_DOWNLOAD_COLLECTIVE_OFFERS_CSV
              )
            }}
            label="Télécharger format CSV"
          />
          <Button
            variant={ButtonVariant.PRIMARY}
            onClick={async () => {
              await downloadHandler(
                'XLS',
                Events.CLICKED_DOWNLOAD_COLLECTIVE_OFFERS_XLS
              )
            }}
            label="Télécharger format Excel"
          />
        </div>
      </DialogBuilder.Footer>
    </DialogBuilder>
  )
}
