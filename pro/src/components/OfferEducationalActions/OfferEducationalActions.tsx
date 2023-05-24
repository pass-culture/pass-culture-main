import cn from 'classnames'
import React from 'react'

import { CollectiveBookingStatus, OfferStatus } from 'apiClient/v1'
import { CollectiveBookingsEvents } from 'core/FirebaseEvents/constants'
import {
  CollectiveOffer,
  CollectiveOfferTemplate,
  isCollectiveOffer,
  Mode,
  patchIsCollectiveOfferActiveAdapter,
  patchIsTemplateOfferActiveAdapter,
} from 'core/OfferEducational'
import useAnalytics from 'hooks/useAnalytics'
import useNotification from 'hooks/useNotification'
import { CircleArrowIcon } from 'icons'
import { getCollectiveStatusLabel } from 'pages/Offers/Offers/OfferItem/Cells/CollectiveOfferStatusCell/CollectiveOfferStatusCell'
import { Button, ButtonLink } from 'ui-kit'
import { ButtonVariant, IconPositionEnum } from 'ui-kit/Button/types'
import {
  FORMAT_ISO_DATE_ONLY,
  formatBrowserTimezonedDateAsUTC,
  toDateStrippedOfTimezone,
} from 'utils/date'

import { ReactComponent as IconActive } from './assets/icon-active.svg'
import { ReactComponent as IconInactive } from './assets/icon-inactive.svg'
import style from './OfferEducationalActions.module.scss'

export interface IOfferEducationalActions {
  className?: string
  isBooked: boolean
  offer: CollectiveOffer | CollectiveOfferTemplate
  mode?: Mode
  reloadCollectiveOffer?: () => void
}

const OfferEducationalActions = ({
  className,
  isBooked,
  offer,
  mode,
  reloadCollectiveOffer,
}: IOfferEducationalActions): JSX.Element => {
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

  const setIsOfferActive = async (isActive: boolean) => {
    const patchAdapter = offer.isTemplate
      ? patchIsTemplateOfferActiveAdapter
      : patchIsCollectiveOfferActiveAdapter
    const { isOk, message } = await patchAdapter({
      isActive,
      offerId: offer.nonHumanizedId,
    })

    if (!isOk) {
      return notify.error(message)
    }

    notify.success(message)
    reloadCollectiveOffer && reloadCollectiveOffer()
  }

  const activateOffer = () => {
    if (offer.isTemplate || offer.isActive) {
      setIsOfferActive(!offer.isActive)
      return
    }

    if (
      !offer.collectiveStock?.bookingLimitDatetime ||
      toDateStrippedOfTimezone(offer.collectiveStock?.bookingLimitDatetime) >
        new Date()
    ) {
      setIsOfferActive(true)
      return
    }
    notify.error(
      'La date limite de réservation est dépassée. Pour publier l’offre, vous devez modifier la date limite de réservation.'
    )
  }

  const shouldShowOfferActions =
    mode === Mode.EDITION || mode === Mode.READ_ONLY

  return (
    <>
      {shouldShowOfferActions && (
        <div className={cn(style['actions'], className)}>
          {!isBooked && offer.status != OfferStatus.EXPIRED && (
            <Button
              Icon={offer.isActive ? IconInactive : IconActive}
              onClick={activateOffer}
              variant={ButtonVariant.TERNARY}
              className={style['button-link']}
              iconPosition={IconPositionEnum.LEFT}
            >
              {offer.isActive
                ? 'Masquer la publication sur Adage'
                : 'Publier sur Adage'}
            </Button>
          )}

          {lastBookingId &&
            (lastBookingStatus != CollectiveBookingStatus.CANCELLED ||
              offer.status == OfferStatus.EXPIRED) && (
              <ButtonLink
                variant={ButtonVariant.TERNARY}
                className={style['button-link']}
                link={{ isExternal: false, to: getBookingLink() }}
                Icon={CircleArrowIcon}
                iconPosition={IconPositionEnum.LEFT}
                onClick={() =>
                  logEvent?.(
                    CollectiveBookingsEvents.CLICKED_SEE_COLLECTIVE_BOOKING,
                    {
                      from: '/offre/collectif/recapitulatif',
                    }
                  )
                }
              >
                Voir la{' '}
                {lastBookingStatus == 'PENDING'
                  ? 'préréservation'
                  : 'réservation'}
              </ButtonLink>
            )}
          {offer.status && (
            <>
              {offer.status != OfferStatus.EXPIRED && (
                <>
                  <div className={style.separator} />{' '}
                </>
              )}
              {getCollectiveStatusLabel(offer.status, lastBookingStatus || '')}
            </>
          )}
        </div>
      )}
    </>
  )
}

export default OfferEducationalActions
