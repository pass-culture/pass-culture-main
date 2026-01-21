import { type JSX, type ReactNode, useState } from 'react'

import type { ShortHighlightResponseModel } from '@/apiClient/v1'
import { useAnalytics } from '@/app/App/analytics/firebase'
import { HighlightEvents } from '@/commons/core/FirebaseEvents/constants'
import { pluralizeFr } from '@/commons/utils/pluralize'
import { Button } from '@/design-system/Button/Button'
import { ButtonColor, ButtonVariant } from '@/design-system/Button/types'
import { Tag, TagVariant } from '@/design-system/Tag/Tag'
import fullEditIcon from '@/icons/full-edit.svg'
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
  const { logEvent } = useAnalytics()

  return (
    <>
      {highlightRequests.length > 0 ? (
        <div className={styles['highlight-banner']}>
          <span className={styles['highlight-banner-content']}>
            <p>
              {pluralizeFr(
                highlightRequests.length,
                'Valorisation à venir :',
                'Valorisations à venir :'
              )}
            </p>
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
              variant={ButtonVariant.TERTIARY}
              color={ButtonColor.BRAND}
              onClick={() => {
                logEvent(HighlightEvents.HAS_CLICKED_EDIT_HIGHLIGHT, {
                  offerId,
                  hightlightIds: highlightRequests.map(
                    (highlightRequest) => highlightRequest.id
                  ),
                })
                setIsOpen(true)
              }}
              icon={fullEditIcon}
            >
              {pluralizeFr(
                highlightRequests.length,
                'Éditer le temps fort',
                'Éditer les temps forts'
              )}
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
              onClick={() => {
                logEvent(HighlightEvents.HAS_CLICKED_CHOOSE_HIGHLIGHT, {
                  offerId,
                })
                setIsOpen(true)
              }}
              label="Choisir un temps fort"
            />
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
