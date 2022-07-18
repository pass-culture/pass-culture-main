import {
  Events,
  OFFER_FORM_NAVIGATION_MEDIUM,
} from 'core/FirebaseEvents/constants'
import { FORMAT_DD_MM_YYYY, toDateStrippedOfTimezone } from 'utils/date'

import { OfferBreadcrumbStep } from 'new_components/OfferBreadcrumb'
import React from 'react'
import { RootState } from 'store/reducers'
import { SummaryLayout } from 'new_components/SummaryLayout'
import { format } from 'date-fns-tz'
import { useSelector } from 'react-redux'

export interface IStockThingSectionProps {
  quantity?: number | null
  price: number
  bookingLimitDatetime: string | null
}

interface IStockThingSummarySection extends IStockThingSectionProps {
  isCreation: boolean
  offerId: string
}

const StockThingSection = ({
  quantity,
  price,
  bookingLimitDatetime,
  isCreation,
  offerId,
}: IStockThingSummarySection): JSX.Element => {
  const editLink = isCreation
    ? `/offre/${offerId}/individuel/creation/stocks`
    : `/offre/${offerId}/individuel/stocks`
  const logEvent = useSelector((state: RootState) => state.app.logEvent)
  const logEditEvent = () => {
    logEvent(Events.CLICKED_OFFER_FORM_NAVIGATION, {
      from: OfferBreadcrumbStep.SUMMARY,
      to: OfferBreadcrumbStep.STOCKS,
      used: OFFER_FORM_NAVIGATION_MEDIUM.RECAP_LINK,
      isEdition: !isCreation,
    })
  }
  return (
    <SummaryLayout.Section
      title="Stocks et prix"
      editLink={editLink}
      onLinkClick={logEditEvent}
    >
      <SummaryLayout.Row title="Prix" description={`${price} €`} />
      {bookingLimitDatetime !== null && (
        <SummaryLayout.Row
          title="Date limite de réservation"
          description={format(
            toDateStrippedOfTimezone(bookingLimitDatetime),
            FORMAT_DD_MM_YYYY
          )}
        />
      )}
      <SummaryLayout.Row
        title="Quantité"
        description={quantity || 'Illimité'}
      />
    </SummaryLayout.Section>
  )
}

export default StockThingSection
