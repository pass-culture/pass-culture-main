import { format } from 'date-fns-tz'
import React from 'react'

import { OfferBreadcrumbStep } from 'components/OfferBreadcrumb'
import { SummaryLayout } from 'components/SummaryLayout'
import {
  Events,
  OFFER_FORM_NAVIGATION_MEDIUM,
} from 'core/FirebaseEvents/constants'
import { OFFER_WIZARD_MODE } from 'core/Offers'
import { useOfferWizardMode } from 'hooks'
import useActiveFeature from 'hooks/useActiveFeature'
import useAnalytics from 'hooks/useAnalytics'
import { FORMAT_DD_MM_YYYY, toDateStrippedOfTimezone } from 'utils/date'

export interface IStockThingSectionProps {
  quantity?: number | null
  price: number
  bookingLimitDatetime: string | null
}

export interface IStockThingSummarySection extends IStockThingSectionProps {
  offerId: string
}

const StockThingSection = ({
  quantity,
  price,
  bookingLimitDatetime,
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
  const mode = useOfferWizardMode()
  const editLink =
    mode === OFFER_WIZARD_MODE.CREATION
      ? stocksUrls.creation
      : stocksUrls.edition
  const { logEvent } = useAnalytics()

  const logEditEvent = () => {
    logEvent?.(Events.CLICKED_OFFER_FORM_NAVIGATION, {
      from: OfferBreadcrumbStep.SUMMARY,
      to: OfferBreadcrumbStep.STOCKS,
      used: OFFER_FORM_NAVIGATION_MEDIUM.RECAP_LINK,
      isEdition: mode === OFFER_WIZARD_MODE.EDITION,
      isDraft: mode !== OFFER_WIZARD_MODE.EDITION,
      offerId: offerId,
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
