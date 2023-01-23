import cn from 'classnames'
import React, { useState } from 'react'

import { OfferStatus } from 'apiClient/v1'
import {
  CollectiveOffer,
  CollectiveOfferTemplate,
  isCollectiveOffer,
} from 'core/OfferEducational'
import useActiveFeature from 'hooks/useActiveFeature'
import { ReactComponent as IcoCircleArrow } from 'icons/ico-circle-arrow.svg'
import { getCollectiveStatusLabel } from 'pages/Offers/Offers/OfferItem/Cells/CollectiveOfferStatusCell/CollectiveOfferStatusCell'
import { Button, ButtonLink } from 'ui-kit'
import { ButtonVariant, IconPositionEnum } from 'ui-kit/Button/types'
import {
  FORMAT_ISO_DATE_ONLY,
  formatBrowserTimezonedDateAsUTC,
  toDateStrippedOfTimezone,
} from 'utils/date'

import CancelCollectiveBookingModal from '../CancelCollectiveBookingModal'

import { ReactComponent as IconActive } from './assets/icon-active.svg'
import { ReactComponent as IconInactive } from './assets/icon-inactive.svg'
import style from './OfferEducationalActions.module.scss'

interface IOfferEducationalActions {
  className?: string
  isOfferActive: boolean
  isBooked: boolean
  offer?: CollectiveOffer | CollectiveOfferTemplate
  setIsOfferActive?(isActive: boolean): void
  cancelActiveBookings?(): void
}

const OfferEducationalActions = ({
  className,
  isOfferActive,
  isBooked,
  offer,
  cancelActiveBookings,
  setIsOfferActive,
}: IOfferEducationalActions): JSX.Element => {
  const [isModalOpen, setIsModalOpen] = useState(false)
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
        toDateStrippedOfTimezone(offerEventDate),
        FORMAT_ISO_DATE_ONLY
      )
      return `/reservations/collectives?page=1&offerEventDate=${eventDateFormated}&bookingStatusFilter=booked&offerType=all&offerVenueId=all&bookingId=${lastBookingId}`
    }
    return ''
  }

  const isImproveCollectiveStatusActive = useActiveFeature(
    'WIP_IMPROVE_COLLECTIVE_STATUS'
  )

  return (
    <>
      {isModalOpen && cancelActiveBookings && (
        <CancelCollectiveBookingModal
          onDismiss={() => setIsModalOpen(false)}
          onValidate={() => {
            cancelActiveBookings()
            setIsModalOpen(false)
          }}
        />
      )}
      <div className={cn(style['actions'], className)}>
        {!isBooked && setIsOfferActive && offer?.status != OfferStatus.EXPIRED && (
          <Button
            Icon={isOfferActive ? IconInactive : IconActive}
            className={style['actions-button']}
            onClick={() => setIsOfferActive(!isOfferActive)}
            variant={ButtonVariant.TERNARY}
          >
            {isOfferActive
              ? 'Masquer la publication sur Adage'
              : 'Publier sur Adage'}
          </Button>
        )}
        {!isImproveCollectiveStatusActive &&
          isBooked &&
          offer?.isCancellable &&
          cancelActiveBookings && (
            <Button
              className={style['actions-button']}
              onClick={() => setIsModalOpen(true)}
              variant={ButtonVariant.SECONDARY}
            >
              Annuler la réservation
            </Button>
          )}
        {isImproveCollectiveStatusActive && lastBookingId && (
          <ButtonLink
            variant={ButtonVariant.TERNARY}
            className={style['button-link']}
            link={{ isExternal: false, to: getBookingLink() }}
            Icon={IcoCircleArrow}
            iconPosition={IconPositionEnum.LEFT}
          >
            Voir la{' '}
            {lastBookingStatus == 'PENDING' ? 'préréservation' : 'réservation'}
          </ButtonLink>
        )}
        {offer?.status && isImproveCollectiveStatusActive && (
          <>
            {offer.status != OfferStatus.EXPIRED && (
              <>
                <div className={style.separator} />{' '}
              </>
            )}
            {getCollectiveStatusLabel(offer?.status, lastBookingStatus || '')}
          </>
        )}
      </div>
    </>
  )
}

export default OfferEducationalActions
