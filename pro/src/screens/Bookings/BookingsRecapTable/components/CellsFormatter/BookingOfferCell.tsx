import cn from 'classnames'
import { format } from 'date-fns-tz'
import React from 'react'

import {
  BookingRecapResponseStockModel,
  CollectiveBookingCollectiveStockResponseModel,
} from 'apiClient/v1'
import { OFFER_WIZARD_STEP_IDS } from 'components/OfferIndividualStepper'
import {
  Events,
  OFFER_FORM_NAVIGATION_IN,
  OFFER_FORM_NAVIGATION_MEDIUM,
} from 'core/FirebaseEvents/constants'
import useAnalytics from 'hooks/useAnalytics'
import { useOfferEditionURL } from 'hooks/useOfferEditionURL'
import { FORMAT_DD_MM_YYYY_HH_mm, toDateStrippedOfTimezone } from 'utils/date'

interface IBookingOfferCellProps {
  offer:
    | BookingRecapResponseStockModel
    | CollectiveBookingCollectiveStockResponseModel
}

const BookingOfferCell = ({ offer }: IBookingOfferCellProps) => {
  const { logEvent } = useAnalytics()
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
          </div>
        ))}
    </>
  )
}

export default BookingOfferCell
