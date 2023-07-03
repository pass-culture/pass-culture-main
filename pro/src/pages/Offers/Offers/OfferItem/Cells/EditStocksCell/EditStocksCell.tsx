import React from 'react'

import { OFFER_WIZARD_STEP_IDS } from 'components/OfferIndividualBreadcrumb'
import {
  Events,
  OFFER_FORM_NAVIGATION_IN,
  OFFER_FORM_NAVIGATION_MEDIUM,
} from 'core/FirebaseEvents/constants'
import { Offer } from 'core/Offers/types'
import useAnalytics from 'hooks/useAnalytics'
import fullStockIcon from 'icons/full-stock.svg'
import ListIconButton from 'ui-kit/ListIconButton/ListIconButton'

const EditStocksCell = ({
  editionStockLink,
  offer,
}: {
  editionStockLink: string
  offer: Offer
}) => {
  const { logEvent } = useAnalytics()

  return (
    <ListIconButton
      onClick={() =>
        logEvent?.(Events.CLICKED_OFFER_FORM_NAVIGATION, {
          from: OFFER_FORM_NAVIGATION_IN.OFFERS,
          to: OFFER_WIZARD_STEP_IDS.STOCKS,
          used: OFFER_FORM_NAVIGATION_MEDIUM.OFFERS_STOCKS,
          isEdition: true,
          offerId: offer.nonHumanizedId,
          isDraft: false,
        })
      }
      url={editionStockLink}
      icon={fullStockIcon}
      hasTooltip
    >
      {offer.isEvent ? `Dates et capacités` : `Stocks`}
    </ListIconButton>
  )
}

export default EditStocksCell
