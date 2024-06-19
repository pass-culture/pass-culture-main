import { format } from 'date-fns-tz'
import React from 'react'

import {
  BookingRecapResponseModel,
  CollectiveBookingResponseModel,
} from 'apiClient/v1'
import { OFFER_STATUS_PENDING } from 'core/Offers/constants'
import { useOfferEditionURL } from 'hooks/useOfferEditionURL'
import fullErrorIcon from 'icons/full-error.svg'
import {
  getDate,
  getRemainingTime,
  shouldDisplayWarning,
} from 'pages/Offers/Offers/OfferItem/Cells/OfferNameCell/utils'
import { SvgIcon } from 'ui-kit/SvgIcon/SvgIcon'
import { FORMAT_DD_MM_YYYY_HH_mm, toDateStrippedOfTimezone } from 'utils/date'
import { formatPrice } from 'utils/formatPrice'
import { pluralize } from 'utils/pluralize'

import styles from './BookingOfferCell.module.scss'

export interface BookingOfferCellProps {
  booking: BookingRecapResponseModel | CollectiveBookingResponseModel
}

export const isCollectiveBooking = (
  booking: BookingRecapResponseModel | CollectiveBookingResponseModel
): booking is CollectiveBookingResponseModel => booking.stock.offerIsEducational

export const BookingOfferCell = ({ booking }: BookingOfferCellProps) => {
  const editionUrl = useOfferEditionURL(
    booking.stock.offerIsEducational,
    booking.stock.offerId,
    false
  )
  const eventBeginningDatetime = booking.stock.eventBeginningDatetime

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
    <div>
      <a
        href={editionUrl}
        title={booking.stock.offerName}
        className={styles['booking-offer-name']}
      >
        {booking.stock.offerName}
      </a>

      {booking.stock.offerIsbn ||
        (eventBeginningDatetime && (
          <div className={styles['booking-offer-additional-info']}>
            {eventDatetimeFormatted || booking.stock.offerIsbn}
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
