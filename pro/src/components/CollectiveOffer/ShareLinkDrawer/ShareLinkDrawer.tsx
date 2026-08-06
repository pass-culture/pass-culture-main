import * as Dialog from '@radix-ui/react-dialog'
import { forwardRef, useState } from 'react'

import { Button } from '@/design-system/Button/Button'
import {
  ButtonColor,
  ButtonSize,
  ButtonVariant,
} from '@/design-system/Button/types'
import connectStrokeIcon from '@/icons/stroke-connect.svg'
import { DialogBuilder } from '@/ui-kit/DialogBuilder/DialogBuilder'

import { ShareTemplateOfferLink } from '../ShareTemplateOfferLink/ShareTemplateOfferLink'
import styles from './ShareLinkDrawer.module.scss'

type ShareLinkDrawerProps = {
  offerId: number
  triggerButtonVariant?: ButtonVariant
  triggerButtonSize?: ButtonSize
  open?: boolean
  onOpenChange?: (open: boolean) => void
  refToFocusOnClose?: React.RefObject<HTMLElement | null>
} & React.ComponentPropsWithoutRef<'button'>

export const ShareLinkDrawer = forwardRef<
  HTMLButtonElement,
  ShareLinkDrawerProps
>(
  (
    {
      offerId,
      triggerButtonVariant,
      triggerButtonSize,
      open,
      onOpenChange,
      refToFocusOnClose,
    },
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
      <DialogBuilder
        variant="drawer"
        onOpenChange={handleOpenChange}
        open={isOpen}
        refToFocusOnClose={refToFocusOnClose}
        title="Aidez les enseignants à retrouver votre offre plus facilement sur ADAGE"
        trigger={
          isControlled ? undefined : (
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
          )
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
  }
)
