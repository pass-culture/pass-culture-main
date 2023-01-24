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
import useActiveFeature from 'hooks/useActiveFeature'
import useAnalytics from 'hooks/useAnalytics'
import { useOfferEditionURL } from 'hooks/useOfferEditionURL'
import {
  getDate,
  getRemainingTime,
  shouldDisplayWarning,
} from 'pages/Offers/Offers/OfferItem/Cells/OfferNameCell/utils'
import Icon from 'ui-kit/Icon/Icon'
import { FORMAT_DD_MM_YYYY_HH_mm, toDateStrippedOfTimezone } from 'utils/date'
import { pluralize } from 'utils/pluralize'

interface IBookingOfferCellProps {
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
}: IBookingOfferCellProps) => {
  const { logEvent } = useAnalytics()
  const isImproveCollectiveStatusActive = useActiveFeature(
    'WIP_IMPROVE_COLLECTIVE_STATUS'
  )

  console.log('ici', offer)
  const editionUrl = useOfferEditionURL(
    offer.offerIsEducational,
    offer.offerIdentifier,
    true
  )
  const eventBeginningDatetime = offer.eventBeginningDatetime
  const isbn = offer.offerIsbn

  const eventDatetimeFormatted = eventBeginningDatetime
    ? format(
        toDateStrippedOfTimezone(eventBeginningDatetime),
        FORMAT_DD_MM_YYYY_HH_mm
      )
    : null

  const shouldShowCollectiveWarning =
    isImproveCollectiveStatusActive &&
    isCollective &&
    bookingRecapInfo.values.booking_status.toUpperCase() ===
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
          className={cn('booking-offer-name', {
            'booking-offer-name-individual': !offer.offerIsEducational,
          })}
        >
          {offer.offerName}
        </div>
      </a>
      {isbn ||
        (eventBeginningDatetime && (
          <div className="booking-offer-additional-info">
            {eventDatetimeFormatted || isbn}
            <span className="stocks">
              {shouldShowCollectiveWarning && (
                <div>
                  <Icon
                    className="sold-out-icon"
                    svg="ico-warning"
                    alt="Attention"
                  />

                  <span className="sold-out-dates">
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
                </div>
              )}
            </span>
          </div>
        ))}
    </>
  )
}

export default BookingOfferCell
