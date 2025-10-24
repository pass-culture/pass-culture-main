import { type JSX, type ReactNode, useState } from 'react'

import type { ShortHighlightResponseModel } from '@/apiClient/v1'
import { Tag, TagVariant } from '@/design-system/Tag/Tag'
import fullEditIcon from '@/icons/full-edit.svg'
import { Button } from '@/ui-kit/Button/Button'
import { ButtonVariant } from '@/ui-kit/Button/types'
import { DialogBuilder } from '@/ui-kit/DialogBuilder/DialogBuilder'

import { OfferHighlightForm } from '../OfferHighlightForm/OfferHighlightForm'
import styles from './OfferHighlightBanner.module.scss'

export type OfferHighlightBannerProps = {
  offerId: number
  highlightRequests: Array<ShortHighlightResponseModel>
}

export const OfferHighlightBanner = ({
  offerId,
  highlightRequests,
}: OfferHighlightBannerProps): JSX.Element => {
  const [isOpen, setIsOpen] = useState(false)

  const isPlural = highlightRequests.length > 1

  return (
    <>
      {highlightRequests.length > 0 ? (
        <div className={styles['highlight-banner']}>
          <span className={styles['highlight-banner-content']}>
            <p>Valorisation{isPlural ? 's' : ''} à venir :</p>
            {highlightRequests.map((request) => (
              <Tag
                variant={TagVariant.NEW}
                key={request.id}
                label={request.name}
              />
            ))}
          </span>
          <OfferHighlightDialogBuilder
            onOpenChange={setIsOpen}
            offerId={offerId}
            isOpen={isOpen}
            highlightRequests={highlightRequests}
          >
            <Button
              variant={ButtonVariant.TERNARYBRAND}
              onClick={() => setIsOpen(true)}
              icon={fullEditIcon}
            >
              Éditer le{isPlural ? 's' : ''} temps fort{isPlural ? 's' : ''}
            </Button>
          </OfferHighlightDialogBuilder>
        </div>
      ) : (
        <div className={styles['no-highlight-banner']}>
          <p className={styles['no-highlight-banner-content']}>
            Valorisez votre évènement en l’associant à un temps fort.
          </p>
          <OfferHighlightDialogBuilder
            onOpenChange={setIsOpen}
            offerId={offerId}
            isOpen={isOpen}
            highlightRequests={[]}
          >
            <Button
              variant={ButtonVariant.PRIMARY}
              onClick={() => setIsOpen(true)}
            >
              Choisir un temps fort
            </Button>
          </OfferHighlightDialogBuilder>
        </div>
      )}
    </>
  )
}

type OfferHighlightDialogBuilderProps = {
  isOpen: boolean
  onOpenChange: (param: boolean) => void
  offerId: number
  highlightRequests: Array<ShortHighlightResponseModel>
  children: ReactNode
}

function OfferHighlightDialogBuilder({
  isOpen,
  onOpenChange,
  offerId,
  children,
  highlightRequests,
}: OfferHighlightDialogBuilderProps) {
  return (
    <DialogBuilder
      open={isOpen}
      onOpenChange={onOpenChange}
      title="Choisir un temps fort"
      variant="drawer"
      trigger={children}
    >
      <OfferHighlightForm
        offerId={offerId}
        highlightRequests={highlightRequests}
        onSuccess={() => onOpenChange(false)}
      />
    </DialogBuilder>
  )
}
