import { type JSX, type ReactNode, useState } from 'react'

import type { ShortHighlightResponseModel } from '@/apiClient/v1'
import { useAnalytics } from '@/app/App/analytics/firebase'
import { HighlightEvents } from '@/commons/core/FirebaseEvents/constants'
import { pluralizeFr } from '@/commons/utils/pluralize'
import { Button } from '@/design-system/Button/Button'
import { ButtonColor, ButtonVariant } from '@/design-system/Button/types'
import fullEditIcon from '@/icons/full-edit.svg'
import strokeEventsIcon from '@/icons/stroke-events.svg'
import { DialogBuilder } from '@/ui-kit/DialogBuilder/DialogBuilder'
import { SvgIcon } from '@/ui-kit/SvgIcon/SvgIcon'

import { OfferHighlightForm } from '../OfferHighlightForm/OfferHighlightForm'
import styles from './OfferHighlightCard.module.scss'

export type OfferHighlightCardProps = {
  offerId: number
  highlightRequests: Array<ShortHighlightResponseModel>
}

export const OfferHighlightCard = ({
  offerId,
  highlightRequests,
}: OfferHighlightCardProps): JSX.Element => {
  const [isOpen, setIsOpen] = useState(false)
  const { logEvent } = useAnalytics()

  const hasHighlights = highlightRequests.length > 0

  return (
    <div className={styles['highlight-card']}>
      <div className={styles['highlight-card-top']}>
        <div className={styles['highlight-card-icon']}>
          <SvgIcon src={strokeEventsIcon} alt="" width="48" />
        </div>
        <p className={styles['highlight-card-text']}>
          Valorisez votre évènement en l’associant à un temps fort.
        </p>
      </div>
      <div className={styles['highlight-card-actions']}>
        <OfferHighlightDialogBuilder
          onOpenChange={setIsOpen}
          offerId={offerId}
          isOpen={isOpen}
          highlightRequests={highlightRequests}
        >
          <Button
            variant={
              hasHighlights ? ButtonVariant.TERTIARY : ButtonVariant.PRIMARY
            }
            color={hasHighlights ? ButtonColor.BRAND : undefined}
            onClick={() => {
              if (hasHighlights) {
                logEvent(HighlightEvents.HAS_CLICKED_EDIT_HIGHLIGHT, {
                  offerId,
                  hightlightIds: highlightRequests.map((r) => r.id),
                })
              } else {
                logEvent(HighlightEvents.HAS_CLICKED_CHOOSE_HIGHLIGHT, {
                  offerId,
                })
              }
              setIsOpen(true)
            }}
            icon={hasHighlights ? fullEditIcon : undefined}
            label={
              hasHighlights
                ? pluralizeFr(
                    highlightRequests.length,
                    'Éditer le temps fort',
                    'Éditer les temps forts'
                  )
                : 'Relier l’offre à un temps fort'
            }
          />
        </OfferHighlightDialogBuilder>
      </div>
    </div>
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
