import cn from 'classnames'
import { type JSX, useState } from 'react'

import { useAnalytics } from '@/app/App/analytics/firebase'
// import { useAnalytics } from '@/app/App/analytics/firebase'
import { useHeadlineOfferContext } from '@/commons/context/HeadlineOfferContext/HeadlineOfferContext'
import { EngagementEvents } from '@/commons/core/FirebaseEvents/constants'
import { useAppSelector } from '@/commons/hooks/useAppSelector'
import { ensureSelectedPartnerVenue } from '@/commons/store/user/selectors'
// import { headlineEvents } from '@/commons/core/FirebaseEvents/constants'
import { Button } from '@/design-system/Button/Button'
import {
  ButtonColor,
  ButtonSize,
  ButtonVariant,
} from '@/design-system/Button/types'
import fullEditIcon from '@/icons/full-edit.svg'
import fullStarIcon from '@/icons/full-star.svg'
import strokeStarIcon from '@/icons/stroke-star.svg'
import { HeadlineOfferImageDialogs } from '@/pages/IndividualOffers/IndividualOffersContainer/components/IndividualOfferColumns/components/HeadlineOfferImageDialogs'
import { ConfirmDialog } from '@/ui-kit/ConfirmDialog/ConfirmDialog'
import { SvgIcon } from '@/ui-kit/SvgIcon/SvgIcon'

import headlineImg from './assets/headline-img.svg'
import styles from './OfferHeadlineCard.module.scss'

type OfferHeadlineCardProps = {
  offerId: number
  hasThumb: boolean
}

export const OfferHeadlineCard = ({
  offerId,
  hasThumb,
}: OfferHeadlineCardProps): JSX.Element | undefined => {
  const { logEvent } = useAnalytics()
  const selectedVenue = useAppSelector(ensureSelectedPartnerVenue)
  const [
    isConfirmDialogReplaceHeadlineOfferOpen,
    setIsConfirmDialogReplaceHeadlineOfferOpen,
  ] = useState(false)
  const [
    isDialogForHeadlineOfferWithoutImageOpen,
    setIsDialogForHeadlineOfferWithoutImageOpen,
  ] = useState(false)

  const { headlineOffer, upsertHeadlineOffer, removeHeadlineOffer } =
    useHeadlineOfferContext()

  const hasHeadlineOffer = !!headlineOffer && headlineOffer.id !== offerId
  const isHeadlineOffer = !!headlineOffer && headlineOffer.id === offerId

  const onConfirmReplaceHeadlineOffer = async () => {
    await upsertHeadlineOffer({
      offerId,
      context: { actionType: 'replace' },
    })
    setIsConfirmDialogReplaceHeadlineOfferOpen(false)
  }

  return (
    <div
      className={cn(styles['headline-card'], {
        [styles['headline-card-edit']]: isHeadlineOffer,
      })}
    >
      <div className={styles['headline-card-top']}>
        {!isHeadlineOffer && (
          <div className={styles['headline-card-icon']}>
            <SvgIcon
              src={headlineImg}
              alt=""
              width="68"
              viewBox="0 0 68 68"
              aria-hidden={true}
            />
          </div>
        )}
        <p className={styles['headline-card-title']}>
          {isHeadlineOffer
            ? 'Votre offre est à la une'
            : 'Ne laissez pas votre offre passer inaperçue : passez-la à la une'}
        </p>
        {isHeadlineOffer && (
          <SvgIcon
            className={styles['headline-card-title-icon']}
            src={fullStarIcon}
            width="16"
            alt=""
            aria-hidden={true}
          />
        )}
      </div>
      {isHeadlineOffer && (
        <p className={styles['headline-card-subtitle']}>
          Elle est mise en avant et affichée en priorité sur votre page dans
          l’application
        </p>
      )}
      <div
        className={cn(styles['headline-card-actions'], {
          [styles['headline-card-actions-edit']]: isHeadlineOffer,
        })}
      >
        <Button
          variant={
            isHeadlineOffer ? ButtonVariant.TERTIARY : ButtonVariant.SECONDARY
          }
          color={ButtonColor.NEUTRAL}
          size={ButtonSize.SMALL}
          onClick={() => {
            if (isHeadlineOffer) {
              removeHeadlineOffer()
              logEvent(EngagementEvents.CLICKED_CONFIRMED_ADD_HEADLINE_OFFER, {
                offerId,
                venueId: selectedVenue.id,
                action: 'deleted',
              })
            } else if (hasHeadlineOffer && hasThumb) {
              setIsConfirmDialogReplaceHeadlineOfferOpen(true)
            } else if (hasHeadlineOffer && !hasThumb) {
              setIsDialogForHeadlineOfferWithoutImageOpen(true)
            } else if (!hasHeadlineOffer && hasThumb) {
              upsertHeadlineOffer({
                offerId,
                context: {
                  actionType: 'add',
                  requiredImageUpload: true,
                },
              })
            } else {
              setIsDialogForHeadlineOfferWithoutImageOpen(true)
            }
          }}
          icon={isHeadlineOffer ? fullEditIcon : undefined}
          label={
            isHeadlineOffer
              ? 'Ne plus mettre à la une'
              : 'Mettre l’offre à la une '
          }
          fullWidth={!isHeadlineOffer}
        />
      </div>

      <ConfirmDialog
        icon={strokeStarIcon}
        cancelText="Annuler"
        confirmText="Confirmer"
        onCancel={() => setIsConfirmDialogReplaceHeadlineOfferOpen(false)}
        onConfirm={onConfirmReplaceHeadlineOffer}
        title={
          'Vous êtes sur le point de remplacer votre offre à la une par une nouvelle offre.'
        }
        open={isConfirmDialogReplaceHeadlineOfferOpen}
      />
      <HeadlineOfferImageDialogs
        offerId={offerId}
        isFirstDialogOpen={isDialogForHeadlineOfferWithoutImageOpen}
        setIsFirstDialogOpen={setIsDialogForHeadlineOfferWithoutImageOpen}
        isInOfferJourney
      />
    </div>
  )
}
