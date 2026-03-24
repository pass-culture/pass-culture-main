import cn from 'classnames'
import { type JSX, useState } from 'react'
import useSWR from 'swr'

import { api } from '@/apiClient/api'
import { useAnalytics } from '@/app/App/analytics/firebase'
import { GET_OFFER_PRO_ADVICE_QUERY_KEY } from '@/commons/config/swrQueryKeys'
import { EngagementEvents } from '@/commons/core/FirebaseEvents/constants'
import { useAppSelector } from '@/commons/hooks/useAppSelector'
import { ensureSelectedVenue } from '@/commons/store/user/selectors'
import { Button } from '@/design-system/Button/Button'
import {
  ButtonColor,
  ButtonSize,
  ButtonVariant,
} from '@/design-system/Button/types'
import fullEditIcon from '@/icons/full-edit.svg'
import { SvgIcon } from '@/ui-kit/SvgIcon/SvgIcon'

import recoImg from './assets/reco-img.svg'
import styles from './OfferRecommendationCard.module.scss'
import { OfferRecommendationDialogBuilder } from './OfferRecommendationDialogBuilder'

type OfferRecommendationCardProps = {
  offerId: number
}

export const OfferRecommendationCard = ({
  offerId,
}: OfferRecommendationCardProps): JSX.Element => {
  const [isOpen, setIsOpen] = useState(false)
  const { logEvent } = useAnalytics()
  const selectedVenue = useAppSelector(ensureSelectedVenue)

  const { data: proAdviceResponse } = useSWR(
    [GET_OFFER_PRO_ADVICE_QUERY_KEY, offerId],
    () => api.getOfferProAdvice(offerId)
  )

  const proAdvice = proAdviceResponse?.proAdvice
  const hasRecommendation = !!proAdvice

  return (
    <div
      className={cn(styles['recommendation-card'], {
        [styles['recommendation-card-edit']]: hasRecommendation,
      })}
    >
      <div className={styles['recommendation-card-top']}>
        {!hasRecommendation && (
          <div className={styles['recommendation-card-icon']}>
            <SvgIcon src={recoImg} alt="" width="68" viewBox="0 0 68 68" />
          </div>
        )}
        <p className={styles['recommendation-card-text']}>
          {hasRecommendation
            ? 'Votre recommandation :'
            : 'Ajoutez une recommandation pour promouvoir votre offre'}
        </p>
      </div>
      {hasRecommendation && (
        <p className={styles['recommendation-card-recommendation']}>
          {proAdvice.content}
        </p>
      )}
      <div>
        <OfferRecommendationDialogBuilder
          onOpenChange={setIsOpen}
          offerId={offerId}
          isOpen={isOpen}
          proAdvice={proAdvice ?? null}
        >
          <Button
            variant={
              hasRecommendation
                ? ButtonVariant.TERTIARY
                : ButtonVariant.SECONDARY
            }
            color={ButtonColor.NEUTRAL}
            size={ButtonSize.SMALL}
            onClick={() => {
              hasRecommendation
                ? logEvent(EngagementEvents.HAS_MADE_RECOMMENDATION, {
                    offerId,
                    venueId: selectedVenue.id,
                    action: 'edited',
                  })
                : logEvent(EngagementEvents.HAS_MADE_RECOMMENDATION, {
                    offerId,
                    venueId: selectedVenue.id,
                    action: 'started',
                  })
              setIsOpen(true)
            }}
            icon={hasRecommendation ? fullEditIcon : undefined}
            label={
              hasRecommendation ? 'Modifier' : 'Ajouter une recommandation'
            }
            fullWidth={!hasRecommendation}
          />
        </OfferRecommendationDialogBuilder>
      </div>
    </div>
  )
}
