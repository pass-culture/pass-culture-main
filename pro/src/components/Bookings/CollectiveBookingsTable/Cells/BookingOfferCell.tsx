import cn from 'classnames'
import { format } from 'date-fns-tz'

import {
  type CollectiveBookingResponseModel,
  OfferStatus,
} from '@/apiClient/v1'
import {
  INDIVIDUAL_OFFER_WIZARD_STEP_IDS,
  OFFER_WIZARD_MODE,
} from '@/commons/core/Offers/constants'
import { getIndividualOfferUrl } from '@/commons/core/Offers/utils/getIndividualOfferUrl'
import { useActiveFeature } from '@/commons/hooks/useActiveFeature'
import {
  FORMAT_DD_MM_YYYY_HH_mm,
  toDateStrippedOfTimezone,
} from '@/commons/utils/date'
import { pluralize } from '@/commons/utils/pluralize'
import {
  getDate,
  getRemainingTime,
  shouldDisplayWarning,
} from '@/components/Bookings/Components/utils/utils'
import fullErrorIcon from '@/icons/full-error.svg'
import { SvgIcon } from '@/ui-kit/SvgIcon/SvgIcon'

import styles from './BookingOfferCell.module.scss'

export interface BookingOfferCellProps {
  booking: CollectiveBookingResponseModel
  className?: string
  isCaledonian?: boolean
}

const isCollectiveBooking = (
  booking: CollectiveBookingResponseModel
): booking is CollectiveBookingResponseModel => booking.stock.offerIsEducational

export const BookingOfferCell = ({
  booking,
  className,
}: BookingOfferCellProps) => {
  const isNewOfferCreationFlowFeatureActive = useActiveFeature(
    'WIP_ENABLE_NEW_OFFER_CREATION_FLOW'
  )

  const offerUrl = booking.stock.offerIsEducational
    ? `/offre/${booking.stock.offerId}/collectif/recapitulatif`
    : getIndividualOfferUrl({
        offerId: booking.stock.offerId,
        mode: OFFER_WIZARD_MODE.READ_ONLY,
        step: isNewOfferCreationFlowFeatureActive
          ? INDIVIDUAL_OFFER_WIZARD_STEP_IDS.DESCRIPTION
          : INDIVIDUAL_OFFER_WIZARD_STEP_IDS.DETAILS,
      })

  const eventBeginningDatetime = booking.stock.eventStartDatetime

  const eventDatetimeFormatted = eventBeginningDatetime
    ? format(
        toDateStrippedOfTimezone(eventBeginningDatetime),
        FORMAT_DD_MM_YYYY_HH_mm
      )
    : null

  const shouldShowCollectiveWarning =
    isCollectiveBooking(booking) &&
    booking.bookingStatus.toUpperCase() === OfferStatus.PENDING &&
    shouldDisplayWarning(booking.stock)

  return (
    <div className={cn(className)}>
      <a
        href={offerUrl}
        className={styles['booking-offer-name']}
        data-testid="booking-offer-name"
      >
        {booking.stock.offerName}
      </a>

      {booking.stock.offerEan ||
        (eventBeginningDatetime && (
          <div className={styles['booking-offer-additional-info']}>
            {eventDatetimeFormatted || booking.stock.offerEan}
            <span className={styles['stocks']}>
              {shouldShowCollectiveWarning && (
                <span>
                  &nbsp;
                  <SvgIcon
                    className={styles['sold-out-icon']}
                    src={fullErrorIcon}
                    alt="Attention"
                  />
                  <span className={styles['sold-out-dates']}>
                    La date limite de réservation par le chef d’établissement
                    est dans{' '}
                    {`${
                      getRemainingTime(booking.stock) >= 1
                        ? pluralize(getRemainingTime(booking.stock), 'jour')
                        : 'moins d’un jour'
                    } (${getDate(booking.stock)})`}
                  </span>
                </span>
              )}
            </span>
          </div>
        ))}
    </div>
  )
}
