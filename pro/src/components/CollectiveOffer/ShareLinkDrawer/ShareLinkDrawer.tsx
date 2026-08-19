import { forwardRef, useState } from 'react'

import { Button } from '@/design-system/Button/Button'
import {
  ButtonColor,
  ButtonSize,
  ButtonVariant,
} from '@/design-system/Button/types'
import { DetailedModal } from '@/design-system/DetailedModal/DetailedModal'
import connectStrokeIcon from '@/icons/stroke-connect.svg'

import { ShareTemplateOfferLink } from '../ShareTemplateOfferLink/ShareTemplateOfferLink'
import styles from './ShareLinkDrawer.module.scss'

type ShareLinkDrawerProps = {
  offerId: number
  triggerButtonVariant?: ButtonVariant
  triggerButtonSize?: ButtonSize
  open?: boolean
  onOpenChange?: (open: boolean) => void
} & React.ComponentPropsWithoutRef<'button'>

export const ShareLinkDrawer = forwardRef<
  HTMLButtonElement,
  ShareLinkDrawerProps
>(
  (
    { offerId, triggerButtonVariant, triggerButtonSize, open, onOpenChange },
    ref
  ) => {
    const [internalOpen, setInternalOpen] = useState(false)
    const isControlled = open !== undefined
    const isOpen = isControlled ? open : internalOpen
    const handleOpenChange = (newOpen: boolean) => {
      if (isControlled) {
        onOpenChange?.(newOpen)
      } else {
        setInternalOpen(newOpen)
      }
    }

    return (
      <>
        {!isControlled && (
          <div className={styles['share-link-container']}>
            <Button
              ref={ref}
              icon={connectStrokeIcon}
              variant={triggerButtonVariant || ButtonVariant.SECONDARY}
              size={triggerButtonSize || ButtonSize.SMALL}
              color={ButtonColor.NEUTRAL}
              label="Partager l’offre"
              onClick={(e) => {
                e.preventDefault()
                setInternalOpen(true)
              }}
            />
          </div>
        )}
        <DetailedModal
          isOpen={isOpen}
          onClose={() => handleOpenChange(false)}
          title="Aidez les enseignants à retrouver votre offre plus facilement sur ADAGE"
          secondaryAction={
            <Button
              variant={ButtonVariant.SECONDARY}
              color={ButtonColor.NEUTRAL}
              onClick={() => handleOpenChange(false)}
              label="Fermer"
            />
          }
          isFooterFixed
        >
          <div className={styles['drawer-content']}>
            <ShareTemplateOfferLink offerId={offerId} />
          </div>
        </DetailedModal>
      </>
    )
  }
)
