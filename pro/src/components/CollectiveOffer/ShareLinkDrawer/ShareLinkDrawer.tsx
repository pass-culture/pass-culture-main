import * as Dialog from '@radix-ui/react-dialog'
import { forwardRef, useState } from 'react'

import { Button } from '@/design-system/Button/Button'
import { ButtonColor, ButtonVariant } from '@/design-system/Button/types'
import { DialogBuilder } from '@/ui-kit/DialogBuilder/DialogBuilder'

import { ShareLinkButton } from '../ShareLinkButton/ShareLinkButton'
import { ShareTemplateOfferLink } from '../ShareTemplateOfferLink/ShareTemplateOfferLink'
import styles from './ShareLinkDrawer.module.scss'

export const ShareLinkDrawer = forwardRef<
  HTMLButtonElement,
  { offerId: number } & React.ComponentPropsWithoutRef<'button'>
>(({ offerId, ...props }, ref) => {
  const [isOpenDialog, setIsOpenDialog] = useState(false)

  return (
    <DialogBuilder
      variant="drawer"
      onOpenChange={setIsOpenDialog}
      open={isOpenDialog}
      title="Aidez les enseignants à retrouver votre offre plus facilement sur ADAGE"
      trigger={<ShareLinkButton ref={ref} {...props} />}
      className={styles['drawer']}
    >
      <div className={styles['drawer-content']}>
        <ShareTemplateOfferLink offerId={offerId} />
      </div>
      <DialogBuilder.Footer>
        <Dialog.Close asChild>
          <Button
            variant={ButtonVariant.SECONDARY}
            color={ButtonColor.NEUTRAL}
            label="Fermer"
          />
        </Dialog.Close>
      </DialogBuilder.Footer>
    </DialogBuilder>
  )
})
