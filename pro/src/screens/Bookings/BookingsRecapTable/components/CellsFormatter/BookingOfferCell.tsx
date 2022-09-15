import cn from 'classnames'
import { format } from 'date-fns-tz'
import React from 'react'

import {
  BookingRecapResponseStockModel,
  CollectiveBookingCollectiveStockResponseModel,
} from 'apiClient/v1'
import useActiveFeature from 'components/hooks/useActiveFeature'
import useAnalytics from 'components/hooks/useAnalytics'
import { useOfferEditionURL } from 'components/hooks/useOfferEditionURL'
import {
  Events,
  OFFER_FORM_NAVIGATION_IN,
  OFFER_FORM_NAVIGATION_MEDIUM,
} from 'core/FirebaseEvents/constants'
import { OfferBreadcrumbStep } from 'new_components/OfferBreadcrumb'
import { FORMAT_DD_MM_YYYY_HH_mm, toDateStrippedOfTimezone } from 'utils/date'

interface IBookingOfferCellProps {
  offer:
    | BookingRecapResponseStockModel
    | CollectiveBookingCollectiveStockResponseModel
}

const BookingOfferCell = ({ offer }: IBookingOfferCellProps) => {
  const { logEvent } = useAnalytics()
  const isOfferFormV3 = useActiveFeature('OFFER_FORM_V3')
  const editionUrl = useOfferEditionURL(
    offer.offer_is_educational,
    offer.offer_identifier,
    isOfferFormV3
  )
  const eventBeginningDatetime = offer.event_beginning_datetime
  const isbn = offer.offer_isbn

  const eventDatetimeFormatted = eventBeginningDatetime
    ? format(
        toDateStrippedOfTimezone(eventBeginningDatetime),
        FORMAT_DD_MM_YYYY_HH_mm
      )
    : null

  return (
    <a
      href={editionUrl}
      rel="noopener noreferrer"
      target="_blank"
      onClick={() =>
        logEvent?.(Events.CLICKED_OFFER_FORM_NAVIGATION, {
          from: OFFER_FORM_NAVIGATION_IN.BOOKINGS,
          to: OfferBreadcrumbStep.SUMMARY,
          used: OFFER_FORM_NAVIGATION_MEDIUM.BOOKINGS_TITLE,
          isEdition: true,
        })
      }
      title={`${offer.offer_name} (ouverture dans un nouvel onglet)`}
    >
      <div
        className={cn('booking-offer-name', {
          'booking-offer-name-individual': !offer.offer_is_educational,
        })}
      >
        {offer.offer_name}
      </div>
      {isbn ||
        (eventBeginningDatetime && (
          <div className="booking-offer-additional-info">
            {eventDatetimeFormatted || isbn}
          </div>
        ))}
    </a>
  )
}

export default BookingOfferCell
