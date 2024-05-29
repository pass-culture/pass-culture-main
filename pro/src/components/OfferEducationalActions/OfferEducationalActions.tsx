import cn from 'classnames'
import { useSWRConfig } from 'swr'

import { api } from 'apiClient/api'
import {
  GetCollectiveOfferResponseModel,
  GetCollectiveOfferTemplateResponseModel,
  CollectiveBookingStatus,
  OfferStatus,
} from 'apiClient/v1'
import { useAnalytics } from 'app/App/analytics/firebase'
import {
  GET_COLLECTIVE_OFFER_QUERY_KEY,
  GET_COLLECTIVE_OFFER_TEMPLATE_QUERY_KEY,
} from 'config/swrQueryKeys'
import { CollectiveBookingsEvents } from 'core/FirebaseEvents/constants'
import {
  offerAdageActivated,
  offerAdageDeactivate,
} from 'core/OfferEducational/constants'
import {
  isCollectiveOffer,
  isCollectiveOfferTemplate,
  Mode,
} from 'core/OfferEducational/types'
import { useNotification } from 'hooks/useNotification'
import fullHideIcon from 'icons/full-hide.svg'
import fullNextIcon from 'icons/full-next.svg'
import strokeCheckIcon from 'icons/stroke-check.svg'
import { getCollectiveStatusLabel } from 'pages/Offers/Offers/OfferItem/Cells/CollectiveOfferStatusCell/CollectiveOfferStatusCell'
import { Button } from 'ui-kit/Button/Button'
import { ButtonLink } from 'ui-kit/Button/ButtonLink'
import { ButtonVariant, IconPositionEnum } from 'ui-kit/Button/types'
import {
  FORMAT_ISO_DATE_ONLY,
  formatBrowserTimezonedDateAsUTC,
  toDateStrippedOfTimezone,
} from 'utils/date'

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
  const lastBookingId = isCollectiveOffer(offer) ? offer.lastBookingId : null
  const lastBookingStatus = isCollectiveOffer(offer)
    ? offer.lastBookingStatus
    : null
  const getBookingLink = () => {
    const offerEventDate =
      isCollectiveOffer(offer) && offer.collectiveStock
        ? offer.collectiveStock.beginningDatetime
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
      notify.success(isActive ? offerAdageActivated : offerAdageDeactivate)
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

  const activateOffer = async () => {
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
    !isBooked &&
    ![OfferStatus.EXPIRED, OfferStatus.PENDING].includes(offer.status)

  const shouldDisplayBookingLink =
    lastBookingId &&
    (lastBookingStatus !== CollectiveBookingStatus.CANCELLED ||
      offer.status === OfferStatus.EXPIRED)

  const shouldDisplayStatusSeparator =
    shouldDisplayAdagePublicationButton || shouldDisplayBookingLink

  return (
    <>
      {shouldShowOfferActions && (
        <div className={cn(style['actions'], className)}>
          {shouldDisplayAdagePublicationButton && (
            <Button
              icon={offer.isActive ? fullHideIcon : strokeCheckIcon}
              onClick={activateOffer}
              variant={ButtonVariant.TERNARY}
              className={style['button-link']}
              iconPosition={IconPositionEnum.LEFT}
            >
              {offer.isActive
                ? 'Masquer la publication sur ADAGE'
                : 'Publier sur ADAGE'}
            </Button>
          )}

          {shouldDisplayBookingLink && (
            <ButtonLink
              variant={ButtonVariant.TERNARY}
              className={style['button-link']}
              link={{ isExternal: false, to: getBookingLink() }}
              icon={fullNextIcon}
              iconPosition={IconPositionEnum.LEFT}
              onClick={() =>
                logEvent(
                  CollectiveBookingsEvents.CLICKED_SEE_COLLECTIVE_BOOKING,
                  {
                    from: '/offre/collectif/recapitulatif',
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
          {shouldDisplayStatusSeparator && (
            <>
              <div className={style.separator} />{' '}
            </>
          )}
          {getCollectiveStatusLabel(offer.status, lastBookingStatus || '')}
        </div>
      )}
    </>
  )
}
