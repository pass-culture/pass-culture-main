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
import {
  isCollectiveOffer,
  isCollectiveOfferTemplate,
  Mode,
} from 'commons/core/OfferEducational/types'
import { useActiveFeature } from 'commons/hooks/useActiveFeature'
import { useNotification } from 'commons/hooks/useNotification'
import { selectCurrentOffererId } from 'commons/store/offerer/selectors'
import {
  FORMAT_ISO_DATE_ONLY,
  formatBrowserTimezonedDateAsUTC,
  isDateValid,
  toDateStrippedOfTimezone,
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
  isBooked: boolean
  offer:
    | GetCollectiveOfferResponseModel
    | GetCollectiveOfferTemplateResponseModel
  mode?: Mode
}

export const OfferEducationalActions = ({
  className,
  isBooked,
  offer,
  mode,
}: OfferEducationalActionsProps): JSX.Element => {
  const { logEvent } = useAnalytics()
  const notify = useNotification()
  const selectedOffererId = useSelector(selectCurrentOffererId)
  const areCollectiveNewStatusesEnabled = useActiveFeature(
    'ENABLE_COLLECTIVE_NEW_STATUSES'
  )
  const lastBookingId = isCollectiveOffer(offer) ? offer.lastBookingId : null
  const lastBookingStatus = isCollectiveOffer(offer)
    ? offer.lastBookingStatus
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

  const isTemplateOfferExpired =
    isDateValid(offer.dates?.end) &&
    new Date(offer.dates.end).getTime() < Date.now()

  const activateOffer = async () => {
    // TODO(anoukhello - 25-10-24) remove this condition when new collective status and actions will be enabled
    // as publish action should not be enable for expired template offers
    if (isTemplateOfferExpired) {
      notify.error(
        "Les dates de l'offre sont dépassées. Pour la publier, vous devez les modifier."
      )
      return
    }
    if (isCollectiveOfferTemplate(offer) || offer.isActive) {
      await setIsOfferActive(!offer.isActive)
      return
    }

    if (
      !offer.collectiveStock?.bookingLimitDatetime ||
      toDateStrippedOfTimezone(offer.collectiveStock.bookingLimitDatetime) >
        new Date()
    ) {
      await setIsOfferActive(true)
      return
    }
    notify.error(
      'La date limite de réservation est dépassée. Pour publier l’offre, vous devez modifier la date limite de réservation.'
    )
  }

  const shouldShowOfferActions =
    mode === Mode.EDITION || mode === Mode.READ_ONLY

  const shouldDisplayAdagePublicationButton =
    !areCollectiveNewStatusesEnabled &&
    !isBooked &&
    ![
      CollectiveOfferDisplayedStatus.EXPIRED,
      CollectiveOfferDisplayedStatus.PENDING,
      CollectiveOfferDisplayedStatus.REJECTED,
      CollectiveOfferDisplayedStatus.ARCHIVED,
    ].includes(offer.displayedStatus)

  const shouldDisplayBookingLink =
    lastBookingId &&
    (lastBookingStatus !== CollectiveBookingStatus.CANCELLED ||
      offer.displayedStatus === CollectiveOfferDisplayedStatus.EXPIRED)

  const canPublishOffer = isActionAllowedOnCollectiveOffer(
    offer,
    CollectiveOfferTemplateAllowedAction.CAN_PUBLISH
  )

  const canHideOffer =
    areCollectiveNewStatusesEnabled &&
    isActionAllowedOnCollectiveOffer(
      offer,
      CollectiveOfferTemplateAllowedAction.CAN_HIDE
    )

  const shouldShowHideButton =
    !areCollectiveNewStatusesEnabled &&
    offer.isActive &&
    !isTemplateOfferExpired

  const publishButtonConfig = shouldShowHideButton
    ? {
        wording: 'Masquer la publication sur ADAGE',
        icon: fullHideIcon,
      }
    : {
        wording: 'Publier sur ADAGE',
        icon: strokeCheckIcon,
      }

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
          {shouldDisplayAdagePublicationButton && (
            <Button
              icon={publishButtonConfig.icon}
              onClick={activateOffer}
              variant={ButtonVariant.TERNARY}
              className={style['button-link']}
              iconPosition={IconPositionEnum.LEFT}
            >
              {publishButtonConfig.wording}
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
