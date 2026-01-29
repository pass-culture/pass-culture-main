import * as Dialog from '@radix-ui/react-dialog'
import { forwardRef, useState } from 'react'

import { Button } from '@/design-system/Button/Button'
import { ButtonColor, ButtonVariant } from '@/design-system/Button/types'
import { Tag, TagVariant } from '@/design-system/Tag/Tag'
import connectStrokeIcon from '@/icons/stroke-connect.svg'
import { DialogBuilder } from '@/ui-kit/DialogBuilder/DialogBuilder'

import { ShareTemplateOfferLink } from '../ShareTemplateOfferLink/ShareTemplateOfferLink'
import styles from './ShareLinkDrawer.module.scss'

export const ShareLinkDrawer = forwardRef<
  HTMLButtonElement,
  { offerId: number } & React.ComponentPropsWithoutRef<'button'>
>(({ offerId }, ref) => {
  const [isOpenDialog, setIsOpenDialog] = useState(false)

  return (
    <DialogBuilder
      variant="drawer"
      onOpenChange={setIsOpenDialog}
      open={isOpenDialog}
      title="Aidez les enseignants à retrouver votre offre plus facilement sur ADAGE"
      trigger={
        <div className={styles['share-link-container']}>
          <Button
            ref={ref}
            icon={connectStrokeIcon}
            variant={ButtonVariant.TERTIARY}
            color={ButtonColor.NEUTRAL}
            label="Partager l’offre"
          />
          <Tag label="Nouveau" variant={TagVariant.NEW} aria-hidden="true" />
        </div>
      }
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
