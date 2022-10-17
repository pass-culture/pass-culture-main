import { format } from 'date-fns-tz'
import React from 'react'

import {
  Events,
  OFFER_FORM_NAVIGATION_MEDIUM,
} from 'core/FirebaseEvents/constants'
import useActiveFeature from 'hooks/useActiveFeature'
import useAnalytics from 'hooks/useAnalytics'
import { OfferBreadcrumbStep } from 'new_components/OfferBreadcrumb'
import { SummaryLayout } from 'new_components/SummaryLayout'
import { FORMAT_DD_MM_YYYY, toDateStrippedOfTimezone } from 'utils/date'

export interface IStockThingSectionProps {
  quantity?: number | null
  price: number
  bookingLimitDatetime: string | null
}

export interface IStockThingSummarySection extends IStockThingSectionProps {
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
  const isOfferFormV3 = useActiveFeature('OFFER_FORM_V3')
  const stocksUrls = isOfferFormV3
    ? {
        creation: `/offre/${offerId}/v3/creation/individuelle/stocks`,
        edition: `/offre/${offerId}/v3/individuelle/stocks`,
      }
    : {
        creation: `/offre/${offerId}/individuel/creation/stocks`,
        edition: `/offre/${offerId}/individuel/stocks`,
      }
  const editLink = isCreation ? stocksUrls.creation : stocksUrls.edition
  const { logEvent } = useAnalytics()

  const logEditEvent = () => {
    logEvent?.(Events.CLICKED_OFFER_FORM_NAVIGATION, {
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
