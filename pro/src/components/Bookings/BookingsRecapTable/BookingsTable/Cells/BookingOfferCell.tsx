import {
  BookingRecapResponseModel,
  CollectiveBookingResponseModel,
} from 'apiClient/v1'
import cn from 'classnames'
import {
  INDIVIDUAL_OFFER_WIZARD_STEP_IDS,
  OFFER_STATUS_PENDING,
  OFFER_WIZARD_MODE,
} from 'commons/core/Offers/constants'
import { getIndividualOfferUrl } from 'commons/core/Offers/utils/getIndividualOfferUrl'
import {
  FORMAT_DD_MM_YYYY_HH_mm,
  toDateStrippedOfTimezone,
} from 'commons/utils/date'
import { formatPrice } from 'commons/utils/formatPrice'
import { pluralize } from 'commons/utils/pluralize'
import {
  getDate,
  getRemainingTime,
  shouldDisplayWarning,
} from 'components/Bookings/BookingsRecapTable/utils/utils'
import { format } from 'date-fns-tz'
import fullErrorIcon from 'icons/full-error.svg'
import { SvgIcon } from 'ui-kit/SvgIcon/SvgIcon'

import styles from './BookingOfferCell.module.scss'

export interface BookingOfferCellProps {
  booking: BookingRecapResponseModel | CollectiveBookingResponseModel
  className?: string
}

export const isCollectiveBooking = (
  booking: BookingRecapResponseModel | CollectiveBookingResponseModel
): booking is CollectiveBookingResponseModel => booking.stock.offerIsEducational

export const BookingOfferCell = ({
  booking,
  className,
}: BookingOfferCellProps) => {
  const offerUrl = booking.stock.offerIsEducational
    ? `/offre/${booking.stock.offerId}/collectif/recapitulatif`
    : getIndividualOfferUrl({
        offerId: booking.stock.offerId,
        mode: OFFER_WIZARD_MODE.READ_ONLY,
        step: INDIVIDUAL_OFFER_WIZARD_STEP_IDS.DETAILS,
      })

  const eventBeginningDatetime = isCollectiveBooking(booking)
    ? booking.stock.eventStartDatetime
    : booking.stock.eventBeginningDatetime

  const eventDatetimeFormatted = eventBeginningDatetime
    ? format(
        toDateStrippedOfTimezone(eventBeginningDatetime),
        FORMAT_DD_MM_YYYY_HH_mm
      )
    : null

  const shouldShowCollectiveWarning =
    isCollectiveBooking(booking) &&
    booking.bookingStatus.toUpperCase() === OFFER_STATUS_PENDING &&
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

      {!isCollectiveBooking(booking) && (
        <div className={styles['tarif']}>
          {booking.bookingPriceCategoryLabel
            ? `${booking.bookingPriceCategoryLabel} - ${formatPrice(
                booking.bookingAmount
              )}`
            : formatPrice(booking.bookingAmount, {
                minimumFractionDigits: 2,
                maximumFractionDigits: 2,
                trailingZeroDisplay: 'stripIfInteger',
              })}
        </div>
      )}
    </div>
  )
}
