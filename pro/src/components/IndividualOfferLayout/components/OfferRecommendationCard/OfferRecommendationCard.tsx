import cn from 'classnames'
import { type JSX, useState } from 'react'
import useSWR from 'swr'

import { apiNew } from '@/apiClient/api'
import { useAnalytics } from '@/app/App/analytics/firebase'
import { GET_OFFER_PRO_ADVICE_QUERY_KEY } from '@/commons/config/swrQueryKeys'
import { EngagementEvents } from '@/commons/core/FirebaseEvents/constants'
import { truncateAtWord } from '@/commons/utils/string'
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
  onSubmit?: () => void
  submitLabel?: string
}

export const OfferRecommendationCard = ({
  offerId,
  onSubmit,
  submitLabel,
}: OfferRecommendationCardProps): JSX.Element => {
  const [isOpen, setIsOpen] = useState(false)
  const { logEvent } = useAnalytics()

  const { data: proAdviceResponse } = useSWR(
    [GET_OFFER_PRO_ADVICE_QUERY_KEY, offerId],
    () => apiNew.getOfferProAdvice({ path: { offer_id: offerId } })
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
            <SvgIcon
              src={recoImg}
              alt=""
              width="68"
              viewBox="0 0 68 68"
              aria-hidden={true}
            />
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
          {truncateAtWord(proAdvice.content, 60)}
          <span className={styles['visually-hidden']}>
            {'pour tout afficher, cliquez sur modifier'}
          </span>
        </p>
      )}
      <div>
        <OfferRecommendationDialogBuilder
          onOpenChange={setIsOpen}
          offerId={offerId}
          isOpen={isOpen}
          proAdvice={proAdvice ?? null}
          onSubmit={onSubmit}
          submitLabel={submitLabel}
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
                    action: 'edited',
                  })
                : logEvent(EngagementEvents.HAS_MADE_RECOMMENDATION, {
                    offerId,
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
