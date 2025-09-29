import cn from 'classnames'
import { format } from 'date-fns-tz'

import type { BookingRecapResponseModel } from '@/apiClient/v1'
import {
  INDIVIDUAL_OFFER_WIZARD_STEP_IDS,
  OFFER_WIZARD_MODE,
} from '@/commons/core/Offers/constants'
import { getIndividualOfferUrl } from '@/commons/core/Offers/utils/getIndividualOfferUrl'
import { useActiveFeature } from '@/commons/hooks/useActiveFeature'
import {
  convertEuroToPacificFranc,
  formatPacificFranc,
} from '@/commons/utils/convertEuroToPacificFranc'
import {
  FORMAT_DD_MM_YYYY_HH_mm,
  toDateStrippedOfTimezone,
} from '@/commons/utils/date'
import { formatPrice } from '@/commons/utils/formatPrice'
import strokeDuoIcon from '@/icons/stroke-duo.svg'
import { SvgIcon } from '@/ui-kit/SvgIcon/SvgIcon'

import styles from './BookingOfferCell.module.scss'

export interface BookingOfferCellProps {
  booking: BookingRecapResponseModel
  isCaledonian?: boolean
}

export const BookingOfferCell = ({
  booking,
  isCaledonian = false,
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
    <div className={cn(styles['offer-details-wrapper'])}>
      <div>
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
      {booking.bookingIsDuo && (
        <SvgIcon
          src={strokeDuoIcon}
          alt="Réservation DUO"
          className={styles['bookings-duo-icon']}
        />
      )}
    </div>
  )
}
