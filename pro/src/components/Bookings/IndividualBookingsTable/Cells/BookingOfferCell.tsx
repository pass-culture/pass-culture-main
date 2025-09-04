import cn from 'classnames'
import { format } from 'date-fns-tz'

import type { BookingRecapResponseModel } from '@/apiClient/v1'
import {
  INDIVIDUAL_OFFER_WIZARD_STEP_IDS,
  OFFER_WIZARD_MODE,
} from '@/commons/core/Offers/constants'
import { getIndividualOfferUrl } from '@/commons/core/Offers/utils/getIndividualOfferUrl'
import {
  convertEuroToPacificFranc,
  formatPacificFranc,
} from '@/commons/utils/convertEuroToPacificFranc'
import {
  FORMAT_DD_MM_YYYY_HH_mm,
  toDateStrippedOfTimezone,
} from '@/commons/utils/date'
import { formatPrice } from '@/commons/utils/formatPrice'

import styles from './BookingOfferCell.module.scss'

export interface BookingOfferCellProps {
  booking: BookingRecapResponseModel
  className?: string
  isCaledonian?: boolean
}

export const BookingOfferCell = ({
  booking,
  className,
  isCaledonian = false,
}: BookingOfferCellProps) => {
  const offerUrl = booking.stock.offerIsEducational
    ? `/offre/${booking.stock.offerId}/collectif/recapitulatif`
    : getIndividualOfferUrl({
        offerId: booking.stock.offerId,
        mode: OFFER_WIZARD_MODE.READ_ONLY,
        step: INDIVIDUAL_OFFER_WIZARD_STEP_IDS.DETAILS,
      })

  const eventBeginningDatetime = booking.stock.eventBeginningDatetime

  const eventDatetimeFormatted = eventBeginningDatetime
    ? format(
        toDateStrippedOfTimezone(eventBeginningDatetime),
        FORMAT_DD_MM_YYYY_HH_mm
      )
    : null

  const formattedPacificFrancPrice = formatPacificFranc(
    convertEuroToPacificFranc(booking.bookingAmount)
  )

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
          </div>
        ))}

      <div className={styles['tarif']}>
        {booking.bookingPriceCategoryLabel
          ? `${booking.bookingPriceCategoryLabel} - ${
              isCaledonian
                ? formattedPacificFrancPrice
                : formatPrice(booking.bookingAmount)
            }`
          : isCaledonian
            ? formattedPacificFrancPrice
            : formatPrice(booking.bookingAmount, {
                minimumFractionDigits: 2,
                maximumFractionDigits: 2,
                trailingZeroDisplay: 'stripIfInteger',
              })}
      </div>
    </div>
  )
}
