import cn from 'classnames'
import { format } from 'date-fns-tz'
import React from 'react'

import {
  BookingRecapResponseModel,
  CollectiveBookingResponseModel,
} from 'apiClient/v1'
import { OFFER_WIZARD_STEP_IDS } from 'components/IndividualOfferBreadcrumb'
import {
  Events,
  OFFER_FORM_NAVIGATION_IN,
  OFFER_FORM_NAVIGATION_MEDIUM,
} from 'core/FirebaseEvents/constants'
import { OFFER_STATUS_PENDING } from 'core/Offers/constants'
import useAnalytics from 'hooks/useAnalytics'
import { useOfferEditionURL } from 'hooks/useOfferEditionURL'
import fullErrorIcon from 'icons/full-error.svg'
import {
  getDate,
  getRemainingTime,
  shouldDisplayWarning,
} from 'pages/Offers/Offers/OfferItem/Cells/OfferNameCell/utils'
import { SvgIcon } from 'ui-kit/SvgIcon/SvgIcon'
import { FORMAT_DD_MM_YYYY_HH_mm, toDateStrippedOfTimezone } from 'utils/date'
import { pluralize } from 'utils/pluralize'

import styles from './BookingOfferCell.module.scss'

export interface BookingOfferCellProps {
  booking: BookingRecapResponseModel | CollectiveBookingResponseModel
}

const isCollectiveBooking = (
  booking: BookingRecapResponseModel | CollectiveBookingResponseModel
): booking is CollectiveBookingResponseModel => booking.stock.offerIsEducational

export const BookingOfferCell = ({ booking }: BookingOfferCellProps) => {
  const { logEvent } = useAnalytics()

  const editionUrl = useOfferEditionURL(
    booking.stock.offerIsEducational,
    booking.stock.offerId,
    true
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
    <>
      <a
        href={editionUrl}
        rel="noopener noreferrer"
        target="_blank"
        onClick={() =>
          logEvent?.(Events.CLICKED_OFFER_FORM_NAVIGATION, {
            from: OFFER_FORM_NAVIGATION_IN.BOOKINGS,
            to: OFFER_WIZARD_STEP_IDS.SUMMARY,
            used: OFFER_FORM_NAVIGATION_MEDIUM.BOOKINGS_TITLE,
            isEdition: true,
          })
        }
        title={`${booking.stock.offerName} (ouverture dans un nouvel onglet)`}
      >
        <div
          className={cn(
            styles['booking-offer-name'],
            !booking.stock.offerIsEducational &&
              styles['booking-offer-name-individual']
          )}
        >
          {booking.stock.offerName}
        </div>
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
                    La date limite de réservation par le chef d'établissement
                    est dans{' '}
                    {`${
                      getRemainingTime(booking.stock) >= 1
                        ? pluralize(getRemainingTime(booking.stock), 'jour')
                        : "moins d'un jour"
                    } (${getDate(booking.stock)})`}
                  </span>
                </span>
              )}
            </span>
          </div>
        ))}
    </>
  )
}
