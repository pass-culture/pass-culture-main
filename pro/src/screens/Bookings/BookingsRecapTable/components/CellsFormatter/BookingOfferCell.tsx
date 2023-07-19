import cn from 'classnames'
import { format } from 'date-fns-tz'
import React from 'react'
import { Row } from 'react-table'

import {
  BookingRecapResponseModel,
  BookingRecapResponseStockModel,
  CollectiveBookingCollectiveStockResponseModel,
  CollectiveBookingResponseModel,
} from 'apiClient/v1'
import { OFFER_WIZARD_STEP_IDS } from 'components/OfferIndividualBreadcrumb'
import {
  Events,
  OFFER_FORM_NAVIGATION_IN,
  OFFER_FORM_NAVIGATION_MEDIUM,
} from 'core/FirebaseEvents/constants'
import { OFFER_STATUS_PENDING } from 'core/Offers'
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

interface BookingOfferCellProps {
  offer:
    | BookingRecapResponseStockModel
    | CollectiveBookingCollectiveStockResponseModel
  bookingRecapInfo:
    | Row<BookingRecapResponseModel>
    | Row<CollectiveBookingResponseModel>
  isCollective: boolean
}

const BookingOfferCell = ({
  offer,
  bookingRecapInfo,
  isCollective,
}: BookingOfferCellProps) => {
  const { logEvent } = useAnalytics()

  const editionUrl = useOfferEditionURL(
    offer.offerIsEducational,
    offer.offerId,
    true
  )
  const eventBeginningDatetime = offer.eventBeginningDatetime

  const eventDatetimeFormatted = eventBeginningDatetime
    ? format(
        toDateStrippedOfTimezone(eventBeginningDatetime),
        FORMAT_DD_MM_YYYY_HH_mm
      )
    : null

  const shouldShowCollectiveWarning =
    isCollective &&
    bookingRecapInfo.values.bookingStatus.toUpperCase() ===
      OFFER_STATUS_PENDING &&
    shouldDisplayWarning([bookingRecapInfo.values.stock])

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
        title={`${offer.offerName} (ouverture dans un nouvel onglet)`}
      >
        <div
          className={cn(
            styles['booking-offer-name'],
            !offer.offerIsEducational && styles['booking-offer-name-individual']
          )}
        >
          {offer.offerName}
        </div>
      </a>
      {offer.offerIsbn ||
        (eventBeginningDatetime && (
          <div className={styles['booking-offer-additional-info']}>
            {eventDatetimeFormatted || offer.offerIsbn}
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
                      getRemainingTime([bookingRecapInfo.values.stock]) >= 1
                        ? pluralize(
                            getRemainingTime([bookingRecapInfo.values.stock]),
                            'jour'
                          )
                        : "moins d'un jour"
                    } (${getDate([bookingRecapInfo.values.stock])})`}
                  </span>
                </span>
              )}
            </span>
          </div>
        ))}
    </>
  )
}

export default BookingOfferCell
