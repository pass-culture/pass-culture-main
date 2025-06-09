import cn from 'classnames'
import { useSelector } from 'react-redux'
import { useSWRConfig } from 'swr'

import { api } from 'apiClient/api'
import {
  CollectiveBookingStatus,
  CollectiveOfferDisplayedStatus,
  CollectiveOfferTemplateAllowedAction,
  GetCollectiveOfferResponseModel,
  GetCollectiveOfferTemplateResponseModel,
} from 'apiClient/v1'
import { useAnalytics } from 'app/App/analytics/firebase'
import {
  GET_COLLECTIVE_OFFER_QUERY_KEY,
  GET_COLLECTIVE_OFFER_TEMPLATE_QUERY_KEY,
} from 'commons/config/swrQueryKeys'
import { CollectiveBookingsEvents } from 'commons/core/FirebaseEvents/constants'
import { isCollectiveOffer, Mode } from 'commons/core/OfferEducational/types'
import { useNotification } from 'commons/hooks/useNotification'
import { selectCurrentOffererId } from 'commons/store/offerer/selectors'
import {
  FORMAT_ISO_DATE_ONLY,
  formatBrowserTimezonedDateAsUTC,
} from 'commons/utils/date'
import { isActionAllowedOnCollectiveOffer } from 'commons/utils/isActionAllowedOnCollectiveOffer'
import { CollectiveStatusLabel } from 'components/CollectiveStatusLabel/CollectiveStatusLabel'
import fullHideIcon from 'icons/full-hide.svg'
import fullNextIcon from 'icons/full-next.svg'
import strokeCheckIcon from 'icons/stroke-check.svg'
import { Button } from 'ui-kit/Button/Button'
import { ButtonLink } from 'ui-kit/Button/ButtonLink'
import { ButtonVariant, IconPositionEnum } from 'ui-kit/Button/types'

import style from './OfferEducationalActions.module.scss'

export interface OfferEducationalActionsProps {
  className?: string
  offer:
    | GetCollectiveOfferResponseModel
    | GetCollectiveOfferTemplateResponseModel
  mode?: Mode
}

export const OfferEducationalActions = ({
  className,
  offer,
  mode,
}: OfferEducationalActionsProps): JSX.Element => {
  const { logEvent } = useAnalytics()
  const notify = useNotification()
  const selectedOffererId = useSelector(selectCurrentOffererId)
  const lastBookingId = isCollectiveOffer(offer) ? offer.booking?.id : null
  const lastBookingStatus = isCollectiveOffer(offer)
    ? offer.booking?.status
    : null
  const getBookingLink = () => {
    const offerEventDate =
      isCollectiveOffer(offer) && offer.collectiveStock
        ? offer.collectiveStock.startDatetime
        : null
    if (offerEventDate && lastBookingId) {
      const eventDateFormated = formatBrowserTimezonedDateAsUTC(
        new Date(offerEventDate),
        FORMAT_ISO_DATE_ONLY
      )
      return `/reservations/collectives?page=1&offerEventDate=${eventDateFormated}&bookingStatusFilter=booked&offerType=all&offerVenueId=all&bookingId=${lastBookingId}`
    }
    // istanbul ignore next: this case should never happen
    return ''
  }

  const { mutate } = useSWRConfig()

  const setIsOfferActive = async (isActive: boolean) => {
    try {
      if (offer.isTemplate) {
        await api.patchCollectiveOffersTemplateActiveStatus({
          ids: [offer.id],
          isActive,
        })
      } else {
        await api.patchCollectiveOffersActiveStatus({
          ids: [offer.id],
          isActive,
        })
      }
      notify.success(
        isActive
          ? 'Votre offre est maintenant active et visible dans ADAGE'
          : 'Votre offre est mise en pause et n’est plus visible sur ADAGE'
      )
    } catch (error) {
      if (error instanceof Error) {
        return notify.error(
          `Une erreur est survenue lors de ${
            isActive ? 'l’activation' : 'la désactivation'
          } de votre offre. ${error.message}`
        )
      } else {
        notify.error(
          `Une  erreur est survenue lors de ${
            isActive ? 'l’activation' : 'la désactivation'
          } de votre offre.`
        )
      }
    }

    await mutate([
      offer.isTemplate
        ? GET_COLLECTIVE_OFFER_TEMPLATE_QUERY_KEY
        : GET_COLLECTIVE_OFFER_QUERY_KEY,
      offer.id,
    ])
  }

  const shouldShowOfferActions =
    mode === Mode.EDITION || mode === Mode.READ_ONLY

  const shouldDisplayBookingLink =
    lastBookingId &&
    (lastBookingStatus !== CollectiveBookingStatus.CANCELLED ||
      offer.displayedStatus === CollectiveOfferDisplayedStatus.EXPIRED)

  const canPublishOffer = isActionAllowedOnCollectiveOffer(
    offer,
    CollectiveOfferTemplateAllowedAction.CAN_PUBLISH
  )

  const canHideOffer = isActionAllowedOnCollectiveOffer(
    offer,
    CollectiveOfferTemplateAllowedAction.CAN_HIDE
  )

  return (
    <>
      {shouldShowOfferActions && (
        <div className={cn(style['actions'], className)}>
          {canHideOffer && (
            <Button
              icon={fullHideIcon}
              onClick={() => setIsOfferActive(false)}
              variant={ButtonVariant.TERNARY}
              className={style['button-link']}
            >
              Mettre en pause
            </Button>
          )}
          {canPublishOffer && (
            <Button
              icon={strokeCheckIcon}
              onClick={() => setIsOfferActive(true)}
              variant={ButtonVariant.TERNARY}
              className={style['button-link']}
            >
              Publier
            </Button>
          )}

          {shouldDisplayBookingLink && (
            <ButtonLink
              variant={ButtonVariant.TERNARY}
              className={style['button-link']}
              to={getBookingLink()}
              icon={fullNextIcon}
              iconPosition={IconPositionEnum.LEFT}
              onClick={() =>
                logEvent(
                  CollectiveBookingsEvents.CLICKED_SEE_COLLECTIVE_BOOKING,
                  {
                    from: '/offre/collectif/recapitulatif',
                    offerId: offer.id,
                    offerType: 'collective',
                    offererId: selectedOffererId?.toString(),
                  }
                )
              }
            >
              Voir la{' '}
              {lastBookingStatus === 'PENDING'
                ? 'préréservation'
                : 'réservation'}
            </ButtonLink>
          )}
          {shouldDisplayBookingLink && (
            <>
              <div className={style.separator} />{' '}
            </>
          )}
          <CollectiveStatusLabel offerDisplayedStatus={offer.displayedStatus} />
        </div>
      )}
    </>
  )
}
