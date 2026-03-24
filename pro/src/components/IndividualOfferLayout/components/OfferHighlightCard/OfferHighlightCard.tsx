import cn from 'classnames'
import { type JSX, useState } from 'react'

import type { ShortHighlightResponseModel } from '@/apiClient/v1'
import { useAnalytics } from '@/app/App/analytics/firebase'
import { EngagementEvents } from '@/commons/core/FirebaseEvents/constants'
import { useAppSelector } from '@/commons/hooks/useAppSelector'
import { ensureSelectedVenue } from '@/commons/store/user/selectors'
import { pluralizeFr } from '@/commons/utils/pluralize'
import { Button } from '@/design-system/Button/Button'
import {
  ButtonColor,
  ButtonSize,
  ButtonVariant,
} from '@/design-system/Button/types'
import { Tag, TagVariant } from '@/design-system/Tag/Tag'
import fullEditIcon from '@/icons/full-edit.svg'
import { SvgIcon } from '@/ui-kit/SvgIcon/SvgIcon'

import highlightImg from './assets/highlight-img.svg'
import styles from './OfferHighlightCard.module.scss'
import { OfferHighlightDialogBuilder } from './OfferHighlightDialogBuilder'

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
  const selectedVenue = useAppSelector(ensureSelectedVenue)

  const hasHighlights = highlightRequests.length > 0

  return (
    <div
      className={cn(styles['highlight-card'], {
        [styles['highlight-card-edit']]: hasHighlights,
      })}
    >
      <div className={styles['highlight-card-top']}>
        {!hasHighlights && (
          <div className={styles['highlight-card-icon']}>
            <SvgIcon src={highlightImg} alt="" width="68" viewBox="0 0 68 68" />
          </div>
        )}
        <p className={styles['highlight-card-text']}>
          {hasHighlights
            ? pluralizeFr(
                highlightRequests.length,
                'Valorisation à venir :',
                'Valorisations à venir :'
              )
            : 'Valorisez votre évènement en l’associant à un temps fort.'}
        </p>
      </div>
      {hasHighlights && (
        <div className={styles['highlight-card-highlights']}>
          {highlightRequests.map((request) => (
            <Tag
              variant={TagVariant.NEW}
              key={request.id}
              label={request.name}
            />
          ))}
        </div>
      )}
      <div
        className={cn(styles['highlight-card-actions'], {
          [styles['highlight-card-actions-edit']]: hasHighlights,
        })}
      >
        <OfferHighlightDialogBuilder
          onOpenChange={setIsOpen}
          offerId={offerId}
          isOpen={isOpen}
          highlightRequests={highlightRequests}
        >
          <Button
            variant={
              hasHighlights ? ButtonVariant.TERTIARY : ButtonVariant.SECONDARY
            }
            color={ButtonColor.NEUTRAL}
            size={ButtonSize.SMALL}
            onClick={() => {
              if (hasHighlights) {
                logEvent(EngagementEvents.HAS_REQUESTED_HIGHLIGHTS, {
                  offerId,
                  venueId: selectedVenue.id,
                  action: 'edited',
                })
              } else {
                logEvent(EngagementEvents.HAS_REQUESTED_HIGHLIGHTS, {
                  offerId,
                  venueId: selectedVenue.id,
                  action: 'started',
                })
              }
              setIsOpen(true)
            }}
            icon={hasHighlights ? fullEditIcon : undefined}
            label={
              hasHighlights ? 'Modifier' : 'Relier l’offre à un temps fort'
            }
            fullWidth={!hasHighlights}
          />
        </OfferHighlightDialogBuilder>
      </div>
    </div>
  )
}
