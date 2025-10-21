import { type JSX, useState } from 'react'

import { Button } from '@/ui-kit/Button/Button'
import { ButtonVariant } from '@/ui-kit/Button/types'
import { DialogBuilder } from '@/ui-kit/DialogBuilder/DialogBuilder'

import { OfferHighlightForm } from '../OfferHighlightForm/OfferHighlightForm'
import styles from './OfferHighlightBanner.module.scss'

interface OfferHighlightBannerProps {
  offerId: number
}

export const OfferHighlightBanner = ({
  offerId,
}: OfferHighlightBannerProps): JSX.Element => {
  const [isOpen, setIsOpen] = useState(false)

  return (
    <div className={styles['highlight-banner']}>
      <p className={styles['highlight-banner-content']}>
        Valorisez votre évènement en l’associant à un temps fort.
      </p>
      <DialogBuilder
        open={isOpen}
        onOpenChange={setIsOpen}
        title="Choisir un temps fort"
        variant="drawer"
        trigger={
          <Button
            variant={ButtonVariant.PRIMARY}
            onClick={() => setIsOpen(true)}
          >
            Choisir un temps fort
          </Button>
        }
      >
        <OfferHighlightForm
          offerId={offerId}
          onSuccess={() => setIsOpen(false)}
        />
      </DialogBuilder>
    </div>
  )
}
